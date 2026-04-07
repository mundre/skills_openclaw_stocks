#!/usr/bin/env python3
"""세션 JSONL 파일 전체 복구 스크립트

Usage:
    python repair-session.py <session_file>
    python repair-session.py <session_file> --dry-run
"""

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# dedup-session.py는 하이픈이 포함된 파일명이라 importlib으로 로드
_scripts_dir = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("dedup_session", _scripts_dir / "dedup-session.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
dedup_session = _mod.dedup_session


def load_lines(session_file: Path) -> List[Tuple[str, Optional[dict]]]:
    """JSONL 파일을 (raw_line, parsed_data) 리스트로 로드"""
    messages = []
    with open(session_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                messages.append((line, data))
            except json.JSONDecodeError:
                messages.append((line, None))
    return messages


def remove_400_errors(messages: List[Tuple[str, Optional[dict]]]) -> Tuple[List[Tuple[str, Optional[dict]]], int]:
    """400 오류 라인과 직전 user 메시지 제거

    조건: isApiErrorMessage==True 또는 error=="invalid_request"
    제거 시 직전 user 메시지도 함께 제거
    """
    removed = 0
    result = []

    for line, data in messages:
        if data is None:
            result.append((line, data))
            continue

        is_error = (
            data.get('isApiErrorMessage') is True
            or data.get('error') == 'invalid_request'
        )

        if is_error:
            # 직전 user 메시지 제거
            if result and result[-1][1] is not None and result[-1][1].get('type') == 'user':
                result.pop()
                removed += 1
            removed += 1
        else:
            result.append((line, data))

    return result, removed


def remove_orphan_tool_results(messages: List[Tuple[str, Optional[dict]]]) -> Tuple[List[Tuple[str, Optional[dict]]], int]:
    """고아 tool_result 탐지 및 제거

    모든 assistant의 tool_use id 수집 → user의 tool_result.tool_use_id가
    매칭 안 되면 해당 user 메시지 삭제
    """
    # 모든 tool_use id 수집
    tool_use_ids = set()
    for _, data in messages:
        if data and data.get('type') == 'assistant':
            content = data.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                        tool_use_ids.add(item.get('id'))

    removed = 0
    result = []

    for line, data in messages:
        if data and data.get('type') == 'user':
            content = data.get('message', {}).get('content', [])
            if isinstance(content, list):
                tool_results = [
                    item for item in content
                    if isinstance(item, dict) and item.get('type') == 'tool_result'
                ]
                if tool_results:
                    all_orphan = all(
                        item.get('tool_use_id') not in tool_use_ids
                        for item in tool_results
                    )
                    if all_orphan:
                        removed += 1
                        continue
        result.append((line, data))

    return result, removed


# 체인 복구에서 제외할 type 목록
_SKIP_CHAIN_TYPES = {'file-history-snapshot', 'queue-operation', 'last-prompt'}


def repair_chains(messages: List[Tuple[str, Optional[dict]]]) -> Tuple[List[Tuple[str, Optional[dict]]], int]:
    """끊어진 체인 복구

    isSidechain==false이고 type이 제외 목록에 없는 메시지에서
    parentUuid 필드가 없으면 이전 메시지의 uuid를 설정
    """
    fixed = 0
    result = []
    prev_uuid = None

    for line, data in messages:
        if data is None or not data.get('uuid'):
            result.append((line, data))
            continue

        msg_type = data.get('type', '')
        is_sidechain = data.get('isSidechain', False)

        if not is_sidechain and msg_type not in _SKIP_CHAIN_TYPES:
            if 'parentUuid' not in data and prev_uuid is not None:
                data = dict(data)
                data['parentUuid'] = prev_uuid
                line = json.dumps(data, ensure_ascii=False)
                fixed += 1

        prev_uuid = data.get('uuid')
        result.append((line, data))

    return result, fixed


def validate(messages: List[Tuple[str, Optional[dict]]]) -> dict:
    """검증: 중복 message.id==0, 고아 tool_result, 끊어진 체인, JSON 유효성"""
    # 중복 message.id 확인 (id==0인 것)
    msg_id_zero_count = 0
    tool_use_ids = set()
    orphan_tool_results = 0
    broken_chains = 0
    invalid_json = 0
    prev_uuid = None

    for line, data in messages:
        if data is None:
            invalid_json += 1
            continue

        # message.id == 0 중복 체크
        msg = data.get('message', {})
        if isinstance(msg, dict) and msg.get('id') == 0:
            msg_id_zero_count += 1

        # tool_use id 수집
        if data.get('type') == 'assistant':
            content = data.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                        tool_use_ids.add(item.get('id'))

        # 고아 tool_result 검사
        if data.get('type') == 'user':
            content = data.get('message', {}).get('content', [])
            if isinstance(content, list):
                tool_results = [
                    item for item in content
                    if isinstance(item, dict) and item.get('type') == 'tool_result'
                ]
                if tool_results:
                    orphans = [
                        item for item in tool_results
                        if item.get('tool_use_id') not in tool_use_ids
                    ]
                    orphan_tool_results += len(orphans)

        # 끊어진 체인 검사
        if data.get('uuid') and not data.get('isSidechain'):
            msg_type = data.get('type', '')
            if msg_type not in _SKIP_CHAIN_TYPES:
                if prev_uuid is not None and 'parentUuid' not in data:
                    broken_chains += 1

        prev_uuid = data.get('uuid')

    return {
        'duplicate_message_id_zero': msg_id_zero_count,
        'orphan_tool_results': orphan_tool_results,
        'broken_chains': broken_chains,
        'invalid_json': invalid_json,
    }


def repair_session(session_file: Path, dry_run: bool = False) -> dict:
    """세션 파일 전체 복구 실행"""
    session_file = Path(session_file)

    if not session_file.exists():
        print(f"Error: {session_file} not found")
        sys.exit(1)

    original_lines = load_lines(session_file)
    original_count = len(original_lines)

    # 1단계: 백업
    if not dry_run:
        bak_file = Path(str(session_file) + '.bak')
        shutil.copy2(session_file, bak_file)
        print(f"[1/6] 백업: {bak_file}")
    else:
        print(f"[1/6] 백업: (dry-run, 건너뜀)")

    # 2단계: dedup
    dedup_result = dedup_session(session_file, dry_run=dry_run)
    dedup_removed = dedup_result['original_lines'] - dedup_result['unique_lines']
    dedup_fixed_chains = dedup_result.get('fixed_chains', 0)

    if not dry_run and 'output_file' in dedup_result:
        dedup_file = Path(dedup_result['output_file'])
        os.replace(dedup_file, session_file)
        print(f"[2/6] dedup: {dedup_removed}개 중복 제거, {dedup_fixed_chains}개 체인 복구 → 적용됨")
    else:
        print(f"[2/6] dedup: {dedup_removed}개 중복 제거, {dedup_fixed_chains}개 체인 복구 (dry-run)")

    # dedup 후 파일 다시 로드
    if not dry_run:
        messages = load_lines(session_file)
    else:
        # dry-run: 원본 그대로 분석
        messages = original_lines

    # 3단계: 400 오류 제거
    messages, error_removed = remove_400_errors(messages)
    print(f"[3/6] 400 오류 제거: {error_removed}개 (오류 라인 + 직전 user 메시지 포함)")

    # 4단계: 고아 tool_result 제거
    messages, orphan_removed = remove_orphan_tool_results(messages)
    print(f"[4/6] 고아 tool_result 제거: {orphan_removed}개")

    # 5단계: 끊어진 체인 복구
    messages, chain_fixed = repair_chains(messages)
    print(f"[5/6] 끊어진 체인 복구: {chain_fixed}개")

    # 6단계: 검증
    validation = validate(messages)
    print(f"[6/6] 검증:")
    print(f"  중복 message.id=0: {validation['duplicate_message_id_zero']}")
    print(f"  고아 tool_result: {validation['orphan_tool_results']}")
    print(f"  끊어진 체인: {validation['broken_chains']}")
    print(f"  JSON 파싱 오류: {validation['invalid_json']}")

    final_count = len(messages)

    # 결과 저장
    if not dry_run and (error_removed > 0 or orphan_removed > 0 or chain_fixed > 0):
        with open(session_file, 'w') as f:
            for line, _ in messages:
                f.write(line + '\n')

    return {
        'original_lines': original_count,
        'final_lines': final_count,
        'dedup_removed': dedup_removed,
        'dedup_fixed_chains': dedup_fixed_chains,
        'error_removed': error_removed,
        'orphan_removed': orphan_removed,
        'chain_fixed': chain_fixed,
        'validation': validation,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    session_file = Path(sys.argv[1])
    dry_run = '--dry-run' in sys.argv

    if not session_file.exists():
        print(f"Error: {session_file} not found")
        sys.exit(1)

    mode = "(dry-run)" if dry_run else ""
    print(f"=== repair-session {mode}: {session_file} ===\n")

    result = repair_session(session_file, dry_run=dry_run)

    print(f"\n=== 결과 ===")
    print(f"원본 라인 수: {result['original_lines']}")
    print(f"최종 라인 수: {result['final_lines']}")
    print(f"총 제거/수정:")
    print(f"  dedup 제거: {result['dedup_removed']}")
    print(f"  dedup 체인 복구: {result['dedup_fixed_chains']}")
    print(f"  400 오류 제거: {result['error_removed']}")
    print(f"  고아 tool_result 제거: {result['orphan_removed']}")
    print(f"  체인 복구: {result['chain_fixed']}")

    v = result['validation']
    ok = all(v[k] == 0 for k in v)
    status = "PASS" if ok else "FAIL"
    print(f"\n검증: {status}")


if __name__ == '__main__':
    main()

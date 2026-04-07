#!/usr/bin/env python3
"""임의 경로의 JSONL 파일들에 dedup을 일괄 실행하여 세션 파일 크기를 줄이는 스크립트

Usage:
    python batch-compress.py <path>                    # 경로 내 *.jsonl 재귀 탐색 + dedup
    python batch-compress.py <path> --dry-run          # 변경 없이 예상 결과만 출력
    python batch-compress.py <path> --clean-orig       # .orig.jsonl 파일도 정리
    python batch-compress.py <path> --clean-proj       # .proj.jsonl 파일도 정리
"""

import os
import sys
import importlib.util
from pathlib import Path


def load_dedup_session():
    """같은 디렉토리의 dedup-session.py에서 dedup_session 함수 import"""
    script_dir = Path(__file__).parent
    dedup_path = script_dir / 'dedup-session.py'

    if not dedup_path.exists():
        print(f"오류: {dedup_path} 파일을 찾을 수 없습니다", file=sys.stderr)
        sys.exit(1)

    spec = importlib.util.spec_from_file_location('dedup_session_mod', dedup_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.dedup_session


def format_size(size_bytes: int) -> str:
    """바이트를 읽기 좋은 형식으로 변환"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / 1024 / 1024:.1f}MB"


def collect_jsonl_files(root: Path) -> list[Path]:
    """경로 내 모든 .jsonl 파일 재귀 탐색 (.orig.jsonl, .proj.jsonl, .dedup 제외)"""
    files = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith('.jsonl') and not (
                fname.endswith('.orig.jsonl') or fname.endswith('.proj.jsonl')
            ):
                files.append(Path(dirpath) / fname)
    return files


def clean_orig_files(root: Path, dry_run: bool) -> tuple[int, int]:
    """
    .orig.jsonl 파일 정리:
    - 대응 .jsonl이 있으면 삭제
    - 대응 .jsonl이 없으면 rename (.orig.jsonl → .jsonl)

    Returns: (deleted, renamed)
    """
    deleted = 0
    renamed = 0

    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            if not fname.endswith('.orig.jsonl'):
                continue
            orig_path = Path(dirpath) / fname
            # .orig.jsonl → .jsonl 대응 파일 경로 계산
            base_name = fname[: -len('.orig.jsonl')] + '.jsonl'
            jsonl_path = Path(dirpath) / base_name

            if jsonl_path.exists():
                print(f"  [orig] 삭제: {orig_path}")
                if not dry_run:
                    orig_path.unlink()
                deleted += 1
            else:
                print(f"  [orig] rename: {orig_path} → {jsonl_path}")
                if not dry_run:
                    orig_path.rename(jsonl_path)
                renamed += 1

    return deleted, renamed


def clean_proj_files(root: Path, dry_run: bool) -> int:
    """
    .proj.jsonl 파일 정리:
    - 대응 .jsonl이 있으면 삭제

    Returns: deleted count
    """
    deleted = 0

    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            if not fname.endswith('.proj.jsonl'):
                continue
            proj_path = Path(dirpath) / fname
            base_name = fname[: -len('.proj.jsonl')] + '.jsonl'
            jsonl_path = Path(dirpath) / base_name

            if jsonl_path.exists():
                print(f"  [proj] 삭제: {proj_path}")
                if not dry_run:
                    proj_path.unlink()
                deleted += 1

    return deleted


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    root = Path(sys.argv[1])
    if not root.exists():
        print(f"오류: {root} 경로가 존재하지 않습니다", file=sys.stderr)
        sys.exit(1)

    dry_run = '--dry-run' in sys.argv
    clean_orig = '--clean-orig' in sys.argv
    clean_proj = '--clean-proj' in sys.argv

    if dry_run:
        print("=== DRY RUN 모드 (파일 변경 없음) ===\n")

    dedup_session = load_dedup_session()

    # 1단계: .orig.jsonl 정리
    if clean_orig:
        print("--- .orig.jsonl 정리 ---")
        orig_deleted, orig_renamed = clean_orig_files(root, dry_run)
        print(f"  삭제: {orig_deleted}개, rename: {orig_renamed}개\n")

    # 2단계: .proj.jsonl 정리
    if clean_proj:
        print("--- .proj.jsonl 정리 ---")
        proj_deleted = clean_proj_files(root, dry_run)
        print(f"  삭제: {proj_deleted}개\n")

    # 3단계: .jsonl 파일 수집 후 크기 역순 정렬 (효과 큰 것 먼저)
    jsonl_files = collect_jsonl_files(root)
    jsonl_files.sort(key=lambda p: p.stat().st_size, reverse=True)

    total = len(jsonl_files)
    if total == 0:
        print("처리할 .jsonl 파일이 없습니다.")
        return

    print(f"--- dedup 처리: {total}개 파일 ---")

    changed = 0
    errors = 0
    total_before = 0
    total_after = 0

    for i, jsonl_path in enumerate(jsonl_files, 1):
        if i % 50 == 0:
            print(f"  진행: {i}/{total} ({changed}개 변경, {errors}개 오류)")

        file_size = jsonl_path.stat().st_size
        total_before += file_size

        try:
            result = dedup_session(jsonl_path, dry_run=dry_run)

            orig_lines = result['original_lines']
            unique_lines = result['unique_lines']
            removed = orig_lines - unique_lines

            if not dry_run and 'output_file' in result:
                dedup_path = Path(result['output_file'])
                after_size = dedup_path.stat().st_size
                total_after += after_size

                if removed > 0:
                    os.replace(dedup_path, jsonl_path)
                    changed += 1
                    print(
                        f"  변경: {jsonl_path.name}"
                        f" ({orig_lines}→{unique_lines}줄,"
                        f" {format_size(file_size)}→{format_size(after_size)})"
                    )
                else:
                    dedup_path.unlink()
                    total_after = total_after - after_size + file_size
            else:
                # dry-run: 라인 비율로 예상 절감량 추정
                if removed > 0 and orig_lines > 0:
                    estimated_after = int(file_size * unique_lines / orig_lines)
                    changed += 1
                    print(
                        f"  [예상 변경] {jsonl_path.name}"
                        f" ({orig_lines}→{unique_lines}줄, -{removed}줄,"
                        f" ~{format_size(file_size - estimated_after)} 절감 예상)"
                    )
                else:
                    estimated_after = file_size
                total_after += estimated_after

        except Exception as e:
            errors += 1
            total_after += file_size
            print(f"  오류: {jsonl_path.name} — {e}", file=sys.stderr)

    # 결과 요약
    saved = total_before - total_after
    ratio = (saved / total_before * 100) if total_before > 0 else 0.0

    print(f"\n{'=== 결과 요약 (DRY RUN) ===' if dry_run else '=== 결과 요약 ==='}")
    print(f"  총 파일:    {total}개")
    print(f"  변경 파일:  {changed}개")
    print(f"  오류:       {errors}개")
    print(f"  처리 전:    {format_size(total_before)}")
    print(f"  처리 후:    {format_size(total_after)}")
    print(f"  절감:       {format_size(saved)} ({ratio:.1f}%)")


if __name__ == '__main__':
    main()

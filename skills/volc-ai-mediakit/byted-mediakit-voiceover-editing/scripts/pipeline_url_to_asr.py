from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

def get_project_root() -> Path:
    # 工程根：与 SKILL_DIR 之间固定相隔两级父目录（<工程根>/<任意>/<任意>/<SKILL_DIR名>/）。
    # 不依赖任何固定目录名字符串；路径过浅时退回 SKILL_DIR 的上一级。
    skill_root = Path(__file__).resolve().parents[1]
    try:
        return skill_root.parents[2]
    except IndexError:
        return skill_root.parent

def _load_skill_env() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    skill_dir = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=skill_dir / ".env", override=False)


_OUTPUT_DIR_OVERRIDE: Path | None = None


def _output_dir() -> Path:
    if _OUTPUT_DIR_OVERRIDE is not None:
        _OUTPUT_DIR_OVERRIDE.mkdir(parents=True, exist_ok=True)
        return _OUTPUT_DIR_OVERRIDE
    out = get_project_root() / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _write_json(name: str, data: Any) -> Path:
    out_path = _output_dir() / name
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def _poll_upload(api, job_ids: List[str], *, interval_s: float = 5.0, max_attempts: int = 240) -> List[Dict[str, Any]]:
    joined = ",".join(job_ids)
    last_urls: List[Dict[str, Any]] = []
    for attempt in range(max_attempts):
        resp = api.query_batch_upload_task_info(joined)
        urls = resp.get("Urls", []) if isinstance(resp, dict) else []
        last_urls = urls
        states: Dict[str, int] = {}
        for u in urls:
            st = (u or {}).get("State", "unknown")
            states[st] = states.get(st, 0) + 1
        print(f"[upload] attempt={attempt+1}/{max_attempts} states={states}")
        done = all((u or {}).get("State") in ("success", "failed") for u in urls) and len(urls) == len(job_ids)
        if done:
            return urls
        time.sleep(interval_s)
    raise TimeoutError("upload polling timeout")


def _poll_vcreative(api, vcreative_id: str, space_name: str, *, interval_s: float = 5.0, max_attempts: int = 240) -> Dict[str, Any]:
    last: Dict[str, Any] = {}
    consecutive_errors = 0
    for attempt in range(max_attempts):
        try:
            last = api.get_v_creative_task_result_once(vcreative_id, space_name)
            consecutive_errors = 0
        except Exception as e:
            msg = str(e)
            retryable = "HTTP 5" in msg or "downstream service error" in msg.lower() or "InternalError" in msg or "CodeN\":1000" in msg
            consecutive_errors += 1
            print(f"[vcreative] attempt={attempt+1}/{max_attempts} transient_error={retryable} err={msg[:220]}")
            if not retryable or consecutive_errors >= 12:
                raise
            sleep_s = min(60.0, interval_s * (2 ** min(4, consecutive_errors - 1)))
            time.sleep(sleep_s)
            continue
        status = last.get("Status") if isinstance(last, dict) else None
        print(f"[vcreative] attempt={attempt+1}/{max_attempts} status={status}")
        if status == "success":
            return last
        if status == "failed_run":
            raise RuntimeError(f"vcreative failed: {json.dumps(last, ensure_ascii=False)[:2000]}")
        time.sleep(interval_s)
    raise TimeoutError("vcreative polling timeout")


def _poll_execution(api, task_type: str, run_id: str, *, interval_s: float = 5.0, max_attempts: int = 240) -> Dict[str, Any]:
    last: Dict[str, Any] = {}
    consecutive_errors = 0
    for attempt in range(max_attempts):
        try:
            last = api.get_media_execution_task_result(task_type, run_id)
            consecutive_errors = 0
        except Exception as e:
            msg = str(e)
            retryable = "HTTP 5" in msg or "downstream service error" in msg.lower() or "InternalError" in msg or "CodeN\":1000" in msg
            consecutive_errors += 1
            print(f"[exec:{task_type}] attempt={attempt+1}/{max_attempts} transient_error={retryable} err={msg[:220]}")
            if not retryable or consecutive_errors >= 12:
                raise
            sleep_s = min(60.0, interval_s * (2 ** min(4, consecutive_errors - 1)))
            time.sleep(sleep_s)
            continue
        status = last.get("Status") if isinstance(last, dict) else None
        print(f"[exec:{task_type}] attempt={attempt+1}/{max_attempts} status={status}")
        if status == "Success":
            return last
        if status in ("Failed", "Fail", "Error"):
            raise RuntimeError(f"execution failed: {json.dumps(last, ensure_ascii=False)[:2000]}")
        time.sleep(interval_s)
    raise TimeoutError(f"execution polling timeout: {task_type}")


def _pick_first_success_upload(urls: List[Dict[str, Any]]) -> Tuple[str, str, str]:
    for u in urls:
        if (u or {}).get("State") == "success":
            space = (u or {}).get("SpaceName") or ""
            vid = (u or {}).get("Vid") or ""
            direct = (u or {}).get("DirectUrl") or ""
            if space and vid:
                return space, vid, direct
    raise RuntimeError("no successful upload item found")


def _normalize_preuploaded_source(source: str) -> Tuple[str, str]:
    s = (source or "").strip()
    if not s:
        raise ValueError("empty source")
    lower = s.lower()
    if lower.startswith("vid://"):
        return "Vid", s.split("://", 1)[1]
    if lower.startswith("directurl://"):
        return "DirectUrl", s.split("://", 1)[1]
    if lower.startswith("v0") and len(s) >= 8 and " " not in s and "/" not in s:
        return "Vid", s
    return "DirectUrl", s


def main() -> None:
    global _OUTPUT_DIR_OVERRIDE
    parser = argparse.ArgumentParser(description="URL/本地文件 -> 上传 -> 提取音频 -> 人声/背景 -> 降噪 -> ASR 转录")
    parser.add_argument("source", nargs="?", help="素材来源：支持 http(s) URL 或本地文件路径")
    parser.add_argument("--ext", default=".mp4", help="FileExtension, 默认 .mp4")
    parser.add_argument("--space", default="", help="SpaceName（默认读取 VOLC_SPACE_NAME）")
    parser.add_argument("--vid", default="", help="直接指定 Vid（跳过上传）")
    parser.add_argument("--directurl", default="", help="直接指定 DirectUrl 文件名（跳过上传）")
    parser.add_argument("--output-dir", default="", help="输出目录，默认 output；可指定 output/<文件名> 或 output/<文件名>(01)")
    args = parser.parse_args()

    if args.output_dir:
        out_str = str(args.output_dir).strip()
        proj_root = get_project_root()
        out_base = (proj_root / "output").resolve()

        cand = Path(out_str)
        if cand.is_absolute():
            resolved = cand.resolve()
            try:
                resolved.relative_to(out_base)
            except ValueError:
                raise SystemExit(f"ERROR: --output-dir 必须在 {out_base} 下：{resolved}")
            _OUTPUT_DIR_OVERRIDE = resolved
        else:
            # 约束：只允许 output/<文件名>（相对路径），拒绝其它相对路径。
            if not out_str.startswith("output/"):
                raise SystemExit("ERROR: --output-dir 只允许传 `output/<文件名>`（相对路径）")
            resolved = (proj_root / out_str).resolve()
            try:
                resolved.relative_to(out_base)
            except ValueError:
                raise SystemExit(f"ERROR: --output-dir 路径越界：{out_str}")
            _OUTPUT_DIR_OVERRIDE = resolved

        _OUTPUT_DIR_OVERRIDE.mkdir(parents=True, exist_ok=True)
    else:
        _OUTPUT_DIR_OVERRIDE = None

    if not args.source and not (getattr(args, "vid", "").strip() or getattr(args, "directurl", "").strip()):
        raise ValueError("缺少 source：请提供素材 URL/本地路径，或使用 --vid / --directurl 跳过上传。")

    # 前置校验：避免链路失败
    if args.source and not ((args.vid or "").strip() or (args.directurl or "").strip()):
        src = (args.source or "").strip()
        if not src.lower().startswith(("vid://", "directurl://")) and not (src.lower().startswith("v0") and len(src) >= 8):
            if src.lower().startswith(("http://", "https://")):
                pass  # URL 格式正确
            elif "://" in src:
                raise ValueError(f"URL 必须以 http:// 或 https:// 开头，当前: {src[:50]}...")
            else:
                p = Path(src)
                if not p.is_file():
                    raise ValueError(f"本地文件不存在: {src}，请确认路径正确或使用 http(s):// 开头的 URL")

    _load_skill_env()
    if not args.space:
        args.space = os.getenv("VOLC_SPACE_NAME", "").strip()

    from api_manage import ApiManage
    from asr_volc import transcribe_audio_url

    if not args.space:
        raise ValueError("space_name is required (set VOLC_SPACE_NAME or pass --space)")

    api = ApiManage()
    space_name = args.space

    # ════════════════════════════════════════════════════════════════
    # Step 1: 上传 / 识别已有素材
    # ════════════════════════════════════════════════════════════════
    asset_type = ""
    asset_value = ""
    vid = ""
    directurl = ""

    if (args.vid or "").strip() or (args.directurl or "").strip():
        if (args.vid or "").strip() and (args.directurl or "").strip():
            raise ValueError("不能同时传 --vid 与 --directurl")
        asset_type = "Vid" if (args.vid or "").strip() else "DirectUrl"
        asset_value = (args.vid or args.directurl).strip()
        print(f"[1] 跳过上传：使用已存在 {asset_type}={asset_value}")
        _write_json("step1_preuploaded.json", {"AssetType": asset_type, "AssetValue": asset_value, "SpaceName": space_name})
    else:
        src = (args.source or "").strip()
        if src.lower().startswith(("vid://", "directurl://")) or (src.lower().startswith("v0") and len(src) >= 8):
            asset_type, asset_value = _normalize_preuploaded_source(src)
            print(f"[1] 跳过上传：识别为 {asset_type}={asset_value}")
            _write_json("step1_preuploaded.json", {"AssetType": asset_type, "AssetValue": asset_value, "SpaceName": space_name})
        else:
            print("[1] 上传素材")
            upload_info = api.upload_media_auto(args.source, space_name=space_name, file_ext=args.ext)
            _write_json("step1_upload_submit.json", upload_info)
            if upload_info.get("type") == "url":
                print("[上传方式] URL 上传")
                job_ids = upload_info.get("JobIds") or []
                if not job_ids:
                    raise RuntimeError(f"Upload returned empty JobIds: {upload_info}")
                urls = _poll_upload(api, job_ids)
                _write_json("step1_upload_query.json", {"Urls": urls})
                space_name, vid, directurl = _pick_first_success_upload(urls)
            else:
                print("[上传方式] 本地文件上传")
                vid = upload_info.get("Vid") or ""
                directurl = upload_info.get("DirectUrl") or ""
                if not vid and not directurl:
                    raise RuntimeError(f"Local upload returned empty Vid/DirectUrl: {upload_info}")
            print(f"[上传成功] Vid={vid} DirectUrl={directurl}")
            asset_type = "Vid" if vid else "DirectUrl"
            asset_value = vid or directurl

    if asset_type == "Vid":
        vid = asset_value
    else:
        directurl = asset_value

    # 补充 PlayURL
    step1_path = _output_dir() / "step1_preuploaded.json"
    step1_data = {}
    if step1_path.is_file():
        step1_data = json.loads(step1_path.read_text(encoding="utf-8"))
    step1_data.update({"AssetType": asset_type, "AssetValue": asset_value, "SpaceName": space_name})
    if asset_type == "Vid":
        step1_data["Vid"] = asset_value
        step1_data["DirectUrl"] = ""
    else:
        step1_data["Vid"] = ""
        step1_data["DirectUrl"] = asset_value
    try:
        step1_data["PlayURL"] = api.get_play_url(type=asset_type.lower(), source=asset_value, space_name=space_name, expired_minutes=60)
    except Exception as e:
        print(f"[警告] 获取视频 PlayURL 失败: {e}")
    _write_json("step1_preuploaded.json", step1_data)

    # ════════════════════════════════════════════════════════════════
    # Step 2: 提取音频
    # ════════════════════════════════════════════════════════════════
    print("[2] 提取音频")
    extract = api.extract_audio(type=asset_type.lower(), source=asset_value, space_name=space_name, format="mp3")
    _write_json("step2_extract_audio_submit.json", extract)
    vcreative_id = extract.get("VCreativeId") or ""
    if not vcreative_id:
        raise RuntimeError(f"extract_audio returned empty VCreativeId: {extract}")
    extract_res = _poll_vcreative(api, vcreative_id, space_name)
    _write_json("step2_extract_audio_result.json", extract_res)
    extracted_filename = ((extract_res.get("OutputJson") or {}).get("filename")) or ""
    print(f"[提取音频] 文件名={extracted_filename}")

    # ════════════════════════════════════════════════════════════════
    # Step 3: 人声/背景分离
    # ════════════════════════════════════════════════════════════════
    print("[3] 人声/背景音分离")
    sep = api.voice_separation_task(type=asset_type, video=asset_value, space_name=space_name)
    _write_json("step3_voice_separation_submit.json", sep)
    run_id = sep.get("RunId") or ""
    if not run_id:
        raise RuntimeError(f"voice_separation_task returned empty RunId: {sep}")
    sep_res = _poll_execution(api, "voiceSeparation", run_id)
    _write_json("step3_voice_separation_result.json", sep_res)

    voice_file = ""
    bg_file = ""
    for a in sep_res.get("AudioUrls", []) or []:
        if (a or {}).get("Type") == "voice":
            voice_file = (a or {}).get("DirectUrl") or ""
        if (a or {}).get("Type") == "background":
            bg_file = (a or {}).get("DirectUrl") or ""
    if not voice_file:
        raise RuntimeError(f"voice separation result missing voice DirectUrl: {sep_res}")
    print(f"[人声分离完成] 人声={voice_file} 背景={bg_file}")

    # ════════════════════════════════════════════════════════════════
    # Step 4: 人声降噪
    # ════════════════════════════════════════════════════════════════
    print("[4] 人声降噪")
    denoise_max_retries = 3
    denoised_file = ""
    for attempt in range(1, denoise_max_retries + 1):
        try:
            denoise = api.audio_noise_reduction_task(type="DirectUrl", audio=voice_file, space_name=space_name)
            _write_json("step4_denoise_submit.json", denoise)
            denoise_run = denoise.get("RunId") or ""
            if not denoise_run:
                raise RuntimeError(f"audio_noise_reduction_task returned empty RunId")
            denoise_res = _poll_execution(api, "audioNoiseReduction", denoise_run)
            _write_json("step4_denoise_result.json", denoise_res)
            for v in denoise_res.get("VideoUrls", []) or []:
                denoised_file = (v or {}).get("DirectUrl") or ""
                if denoised_file:
                    break
            if not denoised_file:
                raise RuntimeError("denoise result missing DirectUrl")
            print(f"[降噪完成] DirectUrl={denoised_file}")
            break
        except Exception as e:
            msg = str(e)
            is_retryable = "500" in msg or "InternalError" in msg.lower()
            if is_retryable and attempt < denoise_max_retries:
                print(f"[降噪] 第 {attempt}/{denoise_max_retries} 次失败，重试...")
                time.sleep(5)
            else:
                print(f"[警告] 降噪失败: {e}，使用原人声文件继续")
                denoised_file = voice_file
                break
    if not denoised_file:
        denoised_file = voice_file

    # ════════════════════════════════════════════════════════════════
    # Step 5: ASR 识别
    # ════════════════════════════════════════════════════════════════
    print("[5] 火山 ASR 识别")
    play_url = api.get_play_url(type="directurl", source=denoised_file, space_name=space_name, expired_minutes=60)
    _write_json("step5_play_url.json", {"PlayURL": play_url, "DirectUrl": denoised_file})
    rid, asr_res = transcribe_audio_url(play_url, audio_type="m4a", output_dir=_output_dir())
    _write_json(f"step5_asr_raw_{rid}.json", asr_res)
    print(f"[ASR 转录完成] 输出: step5_asr_raw_{rid}.json")


if __name__ == "__main__":
    main()

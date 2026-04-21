
#!/usr/bin/env python3
"""
Tencent Cloud MPS AIGC Intelligent Image Generation Script

Features:
  Uses MPS AIGC intelligent content creation to generate images from text descriptions and/or reference images.
  MPS aggregates capabilities from multiple large models (Hunyuan / GEM / Qwen), providing a one-stop API.
  Wraps the CreateAigcImageTask + DescribeAigcImageTask APIs,
  supporting task creation + automatic polling for results.

Supported Models:
  - Hunyuan (Tencent Hunyuan)
  - GEM (supports versions 2.5 / 3.0, supports multi-image input up to 3 images)
  - Qwen (Tongyi Qianwen)

Core Capabilities:
  - Text-to-Image: Generate images from text descriptions
  - Image-to-Image: Generate images from reference images + text descriptions
  - Multi-image reference (GEM only): Up to 3 reference images, supports asset / style reference types
  - Negative Prompt: Exclude unwanted content from generation
  - Enhance Prompt: Automatically optimize prompts to improve results
  - Custom aspect ratio and resolution
  - Store results to COS

COS Storage Configuration (optional):
  Specify the bucket via --cos-bucket-name / --cos-bucket-region / --cos-bucket-path parameters,
  or environment variables TENCENTCLOUD_COS_BUCKET / TENCENTCLOUD_COS_REGION.
  If not configured, MPS default temporary storage is used (images stored for 12 hours).

Usage:
  # Text-to-Image: simplest usage (Hunyuan model)
  python mps_aigc_image.py --prompt "A cute orange cat napping in the sunlight"

  # Specify model and version
  python mps_aigc_image.py --prompt "Cyberpunk city night scene" --model GEM --model-version 3.0

  # Text-to-Image + negative prompt
  python mps_aigc_image.py --prompt "Beautiful landscape painting" --negative-prompt "people, animals, text"

  # Text-to-Image + prompt enhancement
  python mps_aigc_image.py --prompt "Sunset beach" --enhance-prompt

  # Image-to-Image: reference image + description
  python mps_aigc_image.py --prompt "Turn this photo into an oil painting style" \
      --image-url https://example.com/photo.jpg

  # GEM multi-image reference (up to 3 images, supports asset/style reference types)
  python mps_aigc_image.py --prompt "Blend these elements" --model GEM \
      --image-url https://example.com/img1.jpg --image-ref-type asset \
      --image-url https://example.com/img2.jpg --image-ref-type style

  # Specify aspect ratio and resolution
  python mps_aigc_image.py --prompt "Panoramic landscape painting" --aspect-ratio 16:9 --resolution 2K

  # Store to COS
  python mps_aigc_image.py --prompt "Product poster" \
      --cos-bucket-name mybucket-125xxx --cos-bucket-region ap-guangzhou --cos-bucket-path aigc_output

  # Create task only (do not wait for result)
  python mps_aigc_image.py --prompt "Starry sky" --no-wait

  # Query existing task result
  python mps_aigc_image.py --task-id 1234567890-xxxxxxxxxxxxx

  # Dry Run (only print request parameters, do not actually call the API)
  python mps_aigc_image.py --prompt "Test image" --dry-run

Environment Variables:
  TENCENTCLOUD_SECRET_ID   - Tencent Cloud SecretId
  TENCENTCLOUD_SECRET_KEY  - Tencent Cloud SecretKey
  TENCENTCLOUD_COS_BUCKET       - COS Bucket name (optional, for result storage)
  TENCENTCLOUD_COS_REGION       - COS Bucket region (default ap-guangzhou)
"""

import argparse
import json
import os
import sys
import time

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.mps.v20190612 import mps_client, models
except ImportError:
    print("Error: Please install the Tencent Cloud SDK first: pip install tencentcloud-sdk-python", file=sys.stderr)
    sys.exit(1)

# COS SDK (optional, for generating temporary URLs)
try:
    from qcloud_cos import CosConfig, CosS3Client
    _COS_SDK_AVAILABLE = True
except ImportError:
    _COS_SDK_AVAILABLE = False


# =============================================================================
# Model Information
# =============================================================================
SUPPORTED_MODELS = {
    "Hunyuan": {
        "description": "Tencent Hunyuan large model",
        "versions": [],
        "max_images": 1,
    },
    "GEM": {
        "description": "GEM image generation model",
        "versions": ["2.5", "3.0"],
        "max_images": 3,
    },
    "Qwen": {
        "description": "Tongyi Qianwen image generation model",
        "versions": [],
        "max_images": 1,
    },
}

# Supported aspect ratios (GEM model supports the most)
SUPPORTED_ASPECT_RATIOS = [
    "1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
]

# Supported resolutions
SUPPORTED_RESOLUTIONS = ["720P", "1080P", "2K", "4K"]

# Polling configuration
DEFAULT_POLL_INTERVAL = 5   # seconds
DEFAULT_MAX_WAIT = 300      # maximum wait 5 minutes


def get_cos_bucket():
    """Get COS Bucket name from environment variables."""
    return os.environ.get("TENCENTCLOUD_COS_BUCKET", "")


def get_cos_region():
    """Get COS Bucket region from environment variables, default ap-guangzhou."""
    return os.environ.get("TENCENTCLOUD_COS_REGION", "ap-guangzhou")


# =============================================================================
# COS Temporary URL Generation
# =============================================================================
def get_cos_presigned_url(bucket: str, region: str, key: str, 
                          secret_id: str = None, secret_key: str = None,
                          expired: int = 3600) -> str:
    """
    Generate a COS temporary access URL (presigned URL)
    
    Args:
        bucket: COS Bucket name
        region: COS Bucket region
        key: COS object Key
        secret_id: Tencent Cloud SecretId (default: read from environment variables)
        secret_key: Tencent Cloud SecretKey (default: read from environment variables)
        expired: URL validity period (seconds), default 3600 (1 hour)
    
    Returns:
        Presigned URL, returns None on failure
    """
    if not _COS_SDK_AVAILABLE:
        print("Warning: COS SDK is not installed, cannot generate temporary URL. Please install: pip install cos-python-sdk-v5", 
              file=sys.stderr)
        return None
    
    secret_id = secret_id or os.environ.get("TENCENTCLOUD_SECRET_ID")
    secret_key = secret_key or os.environ.get("TENCENTCLOUD_SECRET_KEY")
    
    if not secret_id or not secret_key:
        print("Warning: Missing Tencent Cloud credentials, cannot generate temporary URL", file=sys.stderr)
        return None
    
    try:
        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key
        )
        client = CosS3Client(config)
        
        url = client.get_presigned_url(
            Method='GET',
            Bucket=bucket,
            Key=key,
            Expired=expired
        )
        return url
    except Exception as e:
        print(f"Warning: Failed to generate temporary URL: {e}", file=sys.stderr)
        return None


def resolve_cos_input(cos_bucket: str, cos_region: str, cos_key: str,
                      secret_id: str = None, secret_key: str = None) -> str:
    """
    Resolve a COS path to an accessible URL
    
    Args:
        cos_bucket: COS Bucket name
        cos_region: COS Bucket region
        cos_key: COS object Key
        secret_id: Tencent Cloud SecretId
        secret_key: Tencent Cloud SecretKey
    
    Returns:
        Accessible URL (temporary URL or permanent URL)
    """
    if not cos_bucket or not cos_region or not cos_key:
        return None
    
    # Try to generate a temporary URL
    presigned_url = get_cos_presigned_url(cos_bucket, cos_region, cos_key, 
                                          secret_id, secret_key)
    if presigned_url:
        return presigned_url
    
    # If generation fails, return a permanent URL (may not be accessible)
    return f"https://{cos_bucket}.cos.{cos_region}.myqcloud.com/{cos_key.lstrip('/')}"


try:
    from mps_load_env import ensure_env_loaded as _ensure_env_loaded
    _LOAD_ENV_AVAILABLE = True
except ImportError:
    _LOAD_ENV_AVAILABLE = False
    def _ensure_env_loaded(**kwargs):
        return False

def get_credentials():
    """Get Tencent Cloud credentials from environment variables. If missing, try to auto-load from system files and retry."""
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        # Try to auto-load from system environment variable files
        if _LOAD_ENV_AVAILABLE:
            print("[load_env] Environment variables not set, attempting to auto-load from system files...", file=sys.stderr)
            _ensure_env_loaded(verbose=True)
            secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
            secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
        if not secret_id or not secret_key:
            if _LOAD_ENV_AVAILABLE:
                from mps_load_env import _print_setup_hint, _TARGET_VARS
                _print_setup_hint(["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"])
            else:
                print(
                    "\nError: TENCENTCLOUD_SECRET_ID / TENCENTCLOUD_SECRET_KEY is not set.\n"
                    "Please add these variables to /etc/environment, ~/.profile, or similar files and restart the conversation,\n"
                    "or send the variable values directly in the conversation and let the AI help you configure them.",
                    file=sys.stderr,
                )
            sys.exit(1)
    return credential.Credential(secret_id, secret_key)





def create_mps_client(cred, region):
    """Create an MPS client."""
    http_profile = HttpProfile()
    http_profile.endpoint = "mps.tencentcloudapi.com"
    http_profile.reqMethod = "POST"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile

    return mps_client.MpsClient(cred, region, client_profile)


def build_create_params(args):
    """Build CreateAigcImageTask request parameters."""
    params = {}

    # Model name (required)
    params["ModelName"] = args.model

    # Model version (optional)
    if args.model_version:
        params["ModelVersion"] = args.model_version

    # Prompt
    if args.prompt:
        params["Prompt"] = args.prompt

    # Negative prompt
    if args.negative_prompt:
        params["NegativePrompt"] = args.negative_prompt

    # Prompt enhancement
    if args.enhance_prompt:
        params["EnhancePrompt"] = True

    # Reference images - merge URL and COS path inputs
    image_infos = []
    ref_types = args.image_ref_type or []
    
    # 1. Process directly provided URLs
    if args.image_url:
        for i, url in enumerate(args.image_url):
            info = {"ImageUrl": url}
            if i < len(ref_types):
                info["ReferenceType"] = ref_types[i]
            image_infos.append(info)
    
    # 2. Process COS path inputs - use Cos Input Info structure (recommended, resolves permission issues)
    if args.image_cos_key:
        cos_buckets = args.image_cos_bucket or []
        cos_regions = args.image_cos_region or []
        
        for i, key in enumerate(args.image_cos_key):
            # Get the corresponding bucket and region
            bucket = cos_buckets[i] if i < len(cos_buckets) else (cos_buckets[0] if cos_buckets else None)
            region = cos_regions[i] if i < len(cos_regions) else (cos_regions[0] if cos_regions else "ap-guangzhou")
            
            if not bucket:
                print(f"❌ Error: --image-cos-key[{i}] is missing the corresponding --image-cos-bucket", file=sys.stderr)
                sys.exit(1)
            
            # Use Cos Input Info structure to pass COS path (instead of constructing a URL)
            # This allows MPS to read the file via internal permissions, bypassing public access restrictions
            info = {
                "CosInputInfo": {
                    "Bucket": bucket,
                    "Region": region,
                    "Object": key if key.startswith("/") else f"/{key}"
                }
            }
            # Reference type for COS path input: use ref_types if provided, otherwise leave unset
            url_idx = len(args.image_url) if args.image_url else 0
            ref_type_idx = url_idx + i
            if ref_type_idx < len(ref_types):
                info["ReferenceType"] = ref_types[ref_type_idx]
            image_infos.append(info)
    
    if image_infos:
        params["ImageInfos"] = image_infos

    # Extra parameters
    extra = {}
    if args.aspect_ratio:
        extra["AspectRatio"] = args.aspect_ratio
    if args.resolution:
        extra["Resolution"] = args.resolution
    if extra:
        params["ExtraParameters"] = extra

    # COS storage
    cos_param = build_store_cos_param(args)
    if cos_param:
        params["StoreCosParam"] = cos_param

    # Additional parameters (special scenarios)
    if args.additional_parameters:
        params["AdditionalParameters"] = args.additional_parameters

    # Operator
    if args.operator:
        params["Operator"] = args.operator

    return params


def build_store_cos_param(args):
    """Build COS storage parameters."""
    bucket_name = args.cos_bucket_name or get_cos_bucket()
    bucket_region = args.cos_bucket_region or get_cos_region()

    if not bucket_name:
        return None

    cos_param = {
        "CosBucketName": bucket_name,
        "CosBucketRegion": bucket_region,
    }
    if args.cos_bucket_path:
        cos_param["CosBucketPath"] = args.cos_bucket_path

    return cos_param


def create_aigc_image_task(client, params):
    """Call the CreateAigcImageTask API to create an image generation task."""
    req = models.CreateAigcImageTaskRequest()
    req.from_json_string(json.dumps(params))
    resp = client.CreateAigcImageTask(req)
    return json.loads(resp.to_json_string())


def describe_aigc_image_task(client, task_id):
    """Call the DescribeAigcImageTask API to query task status."""
    req = models.DescribeAigcImageTaskRequest()
    req.from_json_string(json.dumps({"TaskId": task_id}))
    resp = client.DescribeAigcImageTask(req)
    return json.loads(resp.to_json_string())


def poll_task_result(client, task_id, poll_interval, max_wait):
    """Poll and wait for task completion."""
    elapsed = 0
    while elapsed < max_wait:
        result = describe_aigc_image_task(client, task_id)
        status = result.get("Status", "")

        if status == "DONE":
            return result
        elif status == "FAIL":
            message = result.get("Message", "Unknown error")
            print(f"\n❌ Task failed: {message}", file=sys.stderr)
            sys.exit(1)

        # Print progress
        status_text = {"WAIT": "Waiting", "RUN": "Running"}.get(status, status)
        print(f"\r⏳ Task status: {status_text} (elapsed {elapsed}s / max {max_wait}s)", end="", flush=True)

        time.sleep(poll_interval)
        elapsed += poll_interval

    print(f"\n⚠️  Wait timed out (waited {max_wait}s), task is still in progress.", file=sys.stderr)
    print(f"   Please query the result later using --task-id {task_id}.", file=sys.stderr)
    sys.exit(1)


def validate_args(args, parser):
    """Validate arguments."""
    # In query mode, no other parameters are required
    if args.task_id:
        return

    # Create mode: at least one of --prompt, --image-url, or --image-cos-key is required
    has_image_input = bool(args.image_url) or bool(args.image_cos_key)
    if not args.prompt and not has_image_input:
        parser.error("Please specify at least --prompt (text description) or --image-url/--image-cos-key (reference image)")

    # Model version validation
    model_info = SUPPORTED_MODELS.get(args.model)
    if model_info and args.model_version:
        valid_versions = model_info["versions"]
        if valid_versions and args.model_version not in valid_versions:
            parser.error(
                f"Supported versions for model {args.model}: {', '.join(valid_versions)}; "
                f"specified: {args.model_version}"
            )

    # Multi-image reference validation (merge URL and COS path inputs)
    total_images = 0
    if args.image_url:
        total_images += len(args.image_url)
    if args.image_cos_key:
        total_images += len(args.image_cos_key)
    
    if total_images > 0 and model_info:
        max_images = model_info["max_images"]
        if total_images > max_images:
            parser.error(
                f"Model {args.model} supports at most {max_images} reference images; "
                f"{total_images} provided (URL: {len(args.image_url) if args.image_url else 0}, COS: {len(args.image_cos_key) if args.image_cos_key else 0})"
            )

    # image_ref_type count must not exceed total image count
    if args.image_ref_type:
        if len(args.image_ref_type) > total_images:
            parser.error("--image-ref-type count must not exceed the total number of reference images")
    
    # COS path parameter validation
    if args.image_cos_key:
        # Check that bucket is provided
        if not args.image_cos_bucket:
            parser.error("--image-cos-bucket must be specified when using --image-cos-key")
        # If region is provided, count must match key count or be exactly 1
        if args.image_cos_region and len(args.image_cos_region) > 1:
            if len(args.image_cos_region) != len(args.image_cos_key):
                parser.error("--image-cos-region count must match --image-cos-key count, or specify only one")

    # Aspect ratio validation
    if args.aspect_ratio and args.aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
        parser.error(
            f"Unsupported aspect ratio: {args.aspect_ratio}; "
            f"supported: {', '.join(SUPPORTED_ASPECT_RATIOS)}"
        )

    # Resolution validation
    if args.resolution and args.resolution not in SUPPORTED_RESOLUTIONS:
        parser.error(
            f"Unsupported resolution: {args.resolution}; "
            f"supported: {', '.join(SUPPORTED_RESOLUTIONS)}"
        )

    # Additional Parameters JSON format validation
    if args.additional_parameters:
        try:
            json.loads(args.additional_parameters)
        except json.JSONDecodeError:
            parser.error(
                f"--additional-parameters must be a valid JSON string.\n"
                f"Example: '{{\"size\":\"2048x2048\"}}'"
            )





def run(args):
    """Execute the main workflow."""
    region = args.region or os.environ.get("TENCENTCLOUD_API_REGION", "ap-guangzhou")
    cred = get_credentials()
    client = create_mps_client(cred, region)

    # Mode 1: Query an existing task
    if args.task_id:
        print("=" * 60)
        print("Tencent Cloud MPS AIGC Image Generation — Query Task")
        print("=" * 60)
        print(f"TaskId: {args.task_id}")
        print("-" * 60)

        try:
            result = describe_aigc_image_task(client, args.task_id)
            status = result.get("Status", "")
            status_text = {
                "WAIT": "Waiting", "RUN": "Running",
                "DONE": "Completed", "FAIL": "Failed"
            }.get(status, status)

            print(f"Task status: {status_text}")

            if status == "DONE":
                image_urls = result.get("ImageUrls", [])
                print(f"Generated image count: {len(image_urls)}")
                for i, url in enumerate(image_urls, 1):
                    print(f"  Image {i}: {url}")
                print("\n⚠️  Images are stored for 12 hours. Please download them promptly.")
            elif status == "FAIL":
                print(f"Failure reason: {result.get('Message', 'Unknown')}")

            if args.verbose:
                print("\nFull response:")
                print(json.dumps(result, ensure_ascii=False, indent=2))

        except TencentCloudSDKException as e:
            print(f"❌ Query failed: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Mode 2: Create a task
    params = build_create_params(args)

    if args.dry_run:
        print("=" * 60)
        print("[Dry Run Mode] Printing request parameters only — API will not be called")
        print("=" * 60)
        print(json.dumps(params, ensure_ascii=False, indent=2))
        return

    # Print execution info
    print("=" * 60)
    print("Tencent Cloud MPS AIGC Intelligent Image Generation")
    print("=" * 60)
    model_info = SUPPORTED_MODELS.get(args.model, {})
    model_desc = model_info.get("description", args.model)
    print(f"Model: {args.model} ({model_desc})")
    if args.model_version:
        print(f"Version: {args.model_version}")
    if args.prompt:
        prompt_display = args.prompt[:80] + "..." if len(args.prompt) > 80 else args.prompt
        print(f"Prompt: {prompt_display}")
    if args.negative_prompt:
        print(f"Negative prompt: {args.negative_prompt}")
    if args.enhance_prompt:
        print("Prompt enhancement: Enabled")
    
    # Display reference image info (URL + COS path)
    total_images = 0
    if args.image_url:
        total_images += len(args.image_url)
    if args.image_cos_key:
        total_images += len(args.image_cos_key)
    
    if total_images > 0:
        print(f"Reference images: {total_images}")
        # Display direct URLs
        if args.image_url:
            for i, url in enumerate(args.image_url, 1):
                ref_type = ""
                if args.image_ref_type and i - 1 < len(args.image_ref_type):
                    ref_type = f" ({args.image_ref_type[i - 1]})"
                print(f"  Image {i}{ref_type}: {url}")
        # Display COS paths
        if args.image_cos_key:
            start_idx = len(args.image_url) if args.image_url else 0
            for i, key in enumerate(args.image_cos_key, 1):
                idx = start_idx + i
                ref_type = ""
                if args.image_ref_type and idx - 1 < len(args.image_ref_type):
                    ref_type = f" ({args.image_ref_type[idx - 1]})"
                bucket = args.image_cos_bucket[i-1] if i-1 < len(args.image_cos_bucket) else args.image_cos_bucket[0]
                region = args.image_cos_region[i-1] if args.image_cos_region and i-1 < len(args.image_cos_region) else "ap-guangzhou"
                print(f"  Image {idx}{ref_type}: [COS] {bucket}/{region}{key}")
    
    if args.aspect_ratio:
        print(f"Aspect ratio: {args.aspect_ratio}")
    if args.resolution:
        print(f"Resolution: {args.resolution}")
    print("-" * 60)

    if args.verbose:
        print("Request parameters:")
        print(json.dumps(params, ensure_ascii=False, indent=2))
        print()

    try:
        result = create_aigc_image_task(client, params)
        task_id = result.get("TaskId", "N/A")
        request_id = result.get("RequestId", "N/A")

        print(f"✅ AIGC image generation task submitted successfully!")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {request_id}")
        print(f"\n## TaskId: {task_id}")

        if args.no_wait:
            print(f"\nTip: Use the following command to query the task result:")
            print(f"  python mps_aigc_image.py --task-id {task_id}")
            return result

        # Automatically poll and wait for the result
        print(f"\nWaiting for task to complete (poll interval: {args.poll_interval}s, max wait: {args.max_wait}s)...")
        poll_result = poll_task_result(client, task_id, args.poll_interval, args.max_wait)

        image_urls = poll_result.get("ImageUrls", [])
        print(f"\n✅ Task completed! Generated image count: {len(image_urls)}")
        for i, url in enumerate(image_urls, 1):
            print(f"  Image {i}: {url}")
        print("\n⚠️  Images are stored for 12 hours. Please download them promptly.")

        # Automatically download generated images
        download_dir = getattr(args, 'download_dir', None)
        if download_dir and image_urls:
            import urllib.request
            import os as _os
            _os.makedirs(download_dir, exist_ok=True)
            print(f"\n📥 Downloading generated images to: {_os.path.abspath(download_dir)}")
            for i, url in enumerate(image_urls, 1):
                ext = ".jpg"
                local_path = _os.path.join(download_dir, f"aigc_image_{i}{ext}")
                try:
                    urllib.request.urlretrieve(url, local_path)
                    size = _os.path.getsize(local_path)
                    print(f"   [{i}] ✅ {local_path} ({size / 1024:.1f} KB)")
                except Exception as e:
                    print(f"   [{i}] ❌ Download failed: {e}")

        if args.verbose:
            print("\nFull response:")
            print(json.dumps(poll_result, ensure_ascii=False, indent=2))

        return poll_result

    except TencentCloudSDKException as e:
        print(f"❌ Request failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Tencent Cloud MPS AIGC Intelligent Image Generation — One-stop text-to-image and image-to-image powered by Hunyuan, GEM, Qwen, and more",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text-to-image (default Hunyuan model)
  python mps_aigc_image.py --prompt "A cute orange tabby cat napping in the sunlight"

  # Specify GEM model version 3.0
  python mps_aigc_image.py --prompt "Cyberpunk cityscape at night" --model GEM --model-version 3.0

  # Text-to-image with negative prompt and prompt enhancement
  python mps_aigc_image.py --prompt "A beautiful landscape painting" --negative-prompt "people, animals" --enhance-prompt

  # Image-to-image (reference image + description)
  python mps_aigc_image.py --prompt "Oil painting style" --image-url https://example.com/photo.jpg

  # GEM multi-image reference (up to 3 images, with reference types)
  python mps_aigc_image.py --prompt "Blend elements" --model GEM \\
      --image-url https://example.com/img1.jpg --image-ref-type asset \\
      --image-url https://example.com/img2.jpg --image-ref-type style

  # Specify aspect ratio and resolution
  python mps_aigc_image.py --prompt "Panoramic landscape painting" --aspect-ratio 16:9 --resolution 2K

  # Store result to COS
  python mps_aigc_image.py --prompt "Product poster" \\
      --cos-bucket-name mybucket-125xxx --cos-bucket-region ap-guangzhou

  # Query task result
  python mps_aigc_image.py --task-id 1234567890-xxxxxxxxxxxxx

  # Create task without waiting
  python mps_aigc_image.py --prompt "Starry sky" --no-wait

  # Dry Run (print request parameters only)
  python mps_aigc_image.py --prompt "Test" --dry-run

Supported models:
  Hunyuan     Tencent Hunyuan large model (default)
  GEM         GEM image generation model, versions 2.5 / 3.0, supports up to 3 reference images
  Qwen        Qwen image generation model

Aspect ratio options (supported by some models):
  1:1  3:2  2:3  3:4  4:3  4:5  5:4  9:16  16:9  21:9

Resolution options:
  720P  1080P  2K  4K

Environment variables:
  TENCENTCLOUD_SECRET_ID   Tencent Cloud SecretId
  TENCENTCLOUD_SECRET_KEY  Tencent Cloud SecretKey
  TENCENTCLOUD_COS_BUCKET       COS Bucket name (optional, for result storage)
  TENCENTCLOUD_COS_REGION       COS Bucket region (default: ap-guangzhou)
        """
    )

    # ---- Task query ----
    query_group = parser.add_argument_group("Task Query (query an existing task, mutually exclusive with task creation)")
    query_group.add_argument("--task-id", type=str,
                             help="TaskId of an existing task to query")

    # ---- Model configuration ----
    model_group = parser.add_argument_group("Model Configuration")
    model_group.add_argument("--model", type=str, default="Hunyuan",
                             choices=["Hunyuan", "GEM", "Qwen"],
                             help="Model name (default: Hunyuan)")
    model_group.add_argument("--model-version", type=str,
                             help="Model version (e.g., GEM: 2.5 / 3.0)")

    # ---- Image content ----
    content_group = parser.add_argument_group("Image Content")
    content_group.add_argument("--prompt", type=str,
                               help="Image description text (up to 1000 characters). Required when no reference image is provided")
    content_group.add_argument("--negative-prompt", type=str,
                               help="Negative prompt: describe what you do NOT want in the image (supported by some models)")
    content_group.add_argument("--enhance-prompt", action="store_true",
                               help="Enable prompt enhancement: automatically optimizes the prompt to improve generation quality")

    # ---- Reference images ----
    image_group = parser.add_argument_group("Reference Images (optional, for image-to-image)")
    image_group.add_argument("--image-url", type=str, action="append",
                             help="Reference image URL (can be specified multiple times; GEM supports up to 3). Recommended < 7 MB, supports jpeg/png/webp")
    image_group.add_argument("--image-ref-type", type=str, action="append",
                             choices=["asset", "style"],
                             help="Reference type (one-to-one with --image-url): asset=subject reference | style=style reference")
    
    # COS path input (for use after local upload)
    image_group.add_argument("--image-cos-bucket", type=str, action="append",
                             help="COS Bucket containing the reference image (used with --image-cos-region/--image-cos-key, can be specified multiple times)")
    image_group.add_argument("--image-cos-region", type=str, action="append",
                             help="COS Region of the reference image (e.g., ap-guangzhou, one-to-one with --image-cos-key)")
    image_group.add_argument("--image-cos-key", type=str, action="append",
                             help="COS Key of the reference image (e.g., /input/image.jpg, used with --image-cos-bucket/--image-cos-region)")

    # ---- Output configuration ----
    output_group = parser.add_argument_group("Output Configuration")
    output_group.add_argument("--aspect-ratio", type=str,
                              help="Aspect ratio (e.g., 16:9, 1:1, 9:16). Supported options vary by model")
    output_group.add_argument("--resolution", type=str,
                              choices=["720P", "1080P", "2K", "4K"],
                              help="Output resolution (supported by some models)")
    output_group.add_argument("--additional-parameters", type=str,
                              help="Special scene parameters (JSON string), e.g.: '{\"size\":\"2048x2048\"}'")

    # ---- COS storage ----
    cos_group = parser.add_argument_group("COS Storage Configuration (optional; if not configured, MPS temporary storage is used with a 12-hour expiry)")
    cos_group.add_argument("--cos-bucket-name", type=str,
                           help="COS Bucket name (defaults to TENCENTCLOUD_COS_BUCKET environment variable)")
    cos_group.add_argument("--cos-bucket-region", type=str,
                           help="COS Bucket region (defaults to TENCENTCLOUD_COS_REGION environment variable; default: ap-guangzhou)")
    cos_group.add_argument("--cos-bucket-path", type=str, default="/output/aigc-image/",
                          help="Output directory path in the COS bucket (default: /output/aigc-image/)")

    # ---- Execution control ----
    control_group = parser.add_argument_group("Execution Control")
    control_group.add_argument("--no-wait", action="store_true",
                               help="Create the task only, without waiting for the result. Query later with --task-id")
    control_group.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL,
                               help=f"Polling interval in seconds (default: {DEFAULT_POLL_INTERVAL})")
    control_group.add_argument("--max-wait", type=int, default=DEFAULT_MAX_WAIT,
                               help=f"Maximum wait time in seconds (default: {DEFAULT_MAX_WAIT})")
    control_group.add_argument("--operator", type=str,
                               help="Operator name")

    # ---- Other ----
    other_group = parser.add_argument_group("Other Configuration")
    other_group.add_argument("--region", type=str,
                             help="MPS service region (default: ap-guangzhou)")
    other_group.add_argument("--verbose", "-v", action="store_true",
                             help="Enable verbose output")
    other_group.add_argument("--dry-run", action="store_true",
                             help="Print request parameters only without calling the API")
    other_group.add_argument("--download-dir", type=str, default=None,
                             help="Automatically download generated images to the specified directory after task completion (default: disabled; specify a path to enable auto-download)")

    args = parser.parse_args()

    # Validate arguments
    validate_args(args, parser)

    # Execute
    run(args)




if __name__ == "__main__":
    main()
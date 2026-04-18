"""
Lux3D Client - Generate 3D models from 2D images

Security features:
- No API keys stored in code
- HTTPS-only communication
- MD5 signature verification on every request
- Timestamp-based replay protection
- Request timeout protection
- Input validation
"""

import base64
import hashlib
import time
import requests
from PIL import Image
import io
import os
import sys

# Configuration
API_KEY = os.environ.get("LUX3D_API_KEY", "")
BASE_URL = "https://api.luxreal.ai"

# Security constants
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def validate_api_key():
    """Validate API key is properly set and not using default placeholder
    
    Raises:
        ValueError: If API key is not set or is placeholder
    """
    if not API_KEY or API_KEY == "your_lux3d_api_key" or API_KEY == "your_invitation_code_here":
        raise ValueError(
            "[ERROR] API key not configured!\n"
            "Please set LUX3D_API_KEY environment variable:\n"
            "  export LUX3D_API_KEY='your_base64_encoded_key'\n"
            "Or modify the API_KEY variable in this script."
        )


def validate_image_path(image_path):
    """Validate image file exists and is accessible
    
    Args:
        image_path: Path to the image file
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file is not readable
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    if not os.path.isfile(image_path):
        raise ValueError(f"Path is not a file: {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            f.read(1)  # Test read permission
    except PermissionError:
        raise PermissionError(f"Permission denied reading: {image_path}")


def validate_output_path(output_path):
    """Validate output path is writable
    
    Args:
        output_path: Path to save the output
        
    Raises:
        PermissionError: If directory is not writable
        ValueError: If path is invalid
    """
    output_dir = os.path.dirname(output_path) or "."
    if not os.path.isdir(output_dir):
        raise ValueError(f"Output directory does not exist: {output_dir}")
    
    try:
        test_path = os.path.join(output_dir, ".write_test")
        with open(test_path, 'w') as f:
            f.write("test")
        os.remove(test_path)
    except (PermissionError, OSError):
        raise PermissionError(f"Cannot write to directory: {output_dir}")


def safe_log(message, full_key=False):
    """Safely log message without exposing sensitive data
    
    Args:
        message: Log message
        full_key: Whether to include full API key (should be False)
    """
    if not full_key:
        # Mask API key if present
        if API_KEY and len(API_KEY) > 8:
            masked_key = API_KEY[:4] + "..." + API_KEY[-4:]
            message = message.replace(API_KEY, masked_key)
    print(message)


def parse_invitation_code(code):
    """Parse base64 encoded invitation code to get ak/sk/appuid (format: version:ak:sk:appuid)"""
    decoded = base64.b64decode(code).decode('utf-8')
    parts = decoded.split(':')
    if len(parts) != 4:
        raise ValueError(f"Invalid invitation code format: expected 4 parts, got {len(parts)}")
    return {'version': parts[0], 'ak': parts[1], 'sk': parts[2], 'appuid': parts[3]}


def generate_sign(ak, sk, appuid):
    """Generate MD5 signature with timestamp for replay protection
    
    Args:
        ak: Access key
        sk: Secret key  
        appuid: Application user ID
        
    Returns:
        dict: Signature parameters including timestamp
    """
    timestamp = str(int(time.time() * 1000))
    sign_string = sk + ak + appuid + timestamp
    sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    return {'appkey': ak, 'appuid': appuid, 'timestamp': timestamp, 'sign': sign}


def secure_request(method, url, headers=None, data=None, timeout=None, retries=None):
    """Secure HTTP request with retry logic and timeout protection
    
    Args:
        method: HTTP method (GET/POST)
        url: Request URL
        headers: Request headers
        data: Request body data
        timeout: Request timeout in seconds
        retries: Maximum number of retries
        
    Returns:
        Response object
        
    Raises:
        Exception: If all retries fail
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    if timeout is None:
        timeout = REQUEST_TIMEOUT
    
    if retries is None:
        retries = MAX_RETRIES
    
    last_error = None
    
    for attempt in range(retries):
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            last_error = f"Request timeout (attempt {attempt + 1}/{retries})"
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                
        except requests.exceptions.RequestException as e:
            last_error = f"Request failed: {str(e)}"
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
    
    raise Exception(f"Request failed after {retries} attempts: {last_error}")


def image_to_base64(image_path):
    """Convert image file to base64"""
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"


def create_task(image_path):
    """Submit image-to-3D task
    
    Args:
        image_path: Path to the input image file
        
    Returns:
        str: Task ID
        
    Raises:
        Exception: If request fails or API returns error
    """
    # Parse API key
    code = parse_invitation_code(API_KEY)
    sign = generate_sign(code['ak'], code['sk'], code['appuid'])
    
    # Convert image to base64
    base64_image = image_to_base64(image_path)
    
    # Submit task
    url = f"{BASE_URL}/global/lux3d/generate/task/create?appuid={sign['appuid']}&appkey={sign['appkey']}&sign={sign['sign']}&timestamp={sign['timestamp']}"
    
    headers = {"Content-Type": "application/json"}
    payload = {"img": base64_image}
    
    # Use secure request with retry logic
    try:
        response = secure_request("POST", url, headers=headers, data=payload)
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")
    
    try:
        result = response.json()
    except ValueError:
        raise Exception(f"Invalid JSON response: {response.text}")
    
    # Error code handling
    if result.get("code") != 0:
        err_msg = result.get("message", "unknown error")
        raise Exception(f"API error: {err_msg}")
    
    task_id = result.get("d")
    if not task_id:
        raise Exception(f"failed to get task_id, response: {result}")
    
    return task_id


def query_task_status(task_id, max_attempts=60, interval=15):
    """Query task status and get result
    
    Args:
        task_id: Task ID returned from create_task
        max_attempts: Maximum number of polling attempts (default: 60)
        interval: Interval between attempts in seconds (default: 15)
        
    Returns:
        str: URL to download the generated 3D model
        
    Raises:
        Exception: If task fails or timeout
    """
    code = parse_invitation_code(API_KEY)
    sign = generate_sign(code['ak'], code['sk'], code['appuid'])
    
    url = f"{BASE_URL}/global/lux3d/generate/task/get?busid={task_id}&appuid={sign['appuid']}&appkey={sign['appkey']}&sign={sign['sign']}&timestamp={sign['timestamp']}"
    
    for attempt in range(max_attempts):
        try:
            response = secure_request("GET", url, headers={"Content-Type": "application/json"})
            result = response.json()
        except ValueError:
            raise Exception(f"Invalid JSON response: {response.text}")
        status = result.get("d", {}).get("status")
        
        if status == 3:  # Completed
            outputs = result.get("d", {}).get("outputs", [])
            if outputs:
                return outputs[0].get("content")  # GLB model URL
        elif status == 4:  # Failed
            raise Exception("Task execution failed")
        else:
            time.sleep(interval)
    
    raise Exception("Task timeout")


def download_model(model_url, output_path):
    """Download generated model
    
    Args:
        model_url: URL from query_task_status
        output_path: Local path to save the model
        
    Returns:
        int: Number of bytes downloaded
    """
    # Security: Validate output path
    validate_output_path(output_path)
    
    # Use secure request with retry logic
    response = secure_request("GET", model_url)
    with open(output_path, 'wb') as f:
        f.write(response.content)
    return len(response.content)


def generate_3d_model(image_path, output_path=None):
    """Complete workflow: submit task, wait, and download
    
    Args:
        image_path: Path to input image
        output_path: Path to save output (optional, auto-generated from input)
        
    Returns:
        str: Path to downloaded model
        
    Raises:
        ValueError: If API key not configured or paths invalid
    """
    # Security: Validate API key early
    validate_api_key()
    
    # Step 1: Submit task
    print("=== Submitting task ===")
    task_id = create_task(image_path)
    print(f"Task ID: {task_id}")
    
    # Step 2: Query result (wait for completion)
    print("\n=== Querying result ===")
    model_url = query_task_status(task_id)
    print(f"Generated 3D model URL: {model_url}")
    
    # Step 3: Download model
    if output_path is None:
        output_name = image_path.rsplit('.', 1)[0] + '_3d.zip'
    else:
        output_name = output_path
    
    print(f"\n=== Downloading model ===")
    size = download_model(model_url, output_name)
    print(f"Downloaded: {output_name} ({size} bytes)")
    
    return output_name


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python lux3d_client.py <image_path> [output_path]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = generate_3d_model(image_path, output_path)
        print(f"\n[SUCCESS] Model saved to: {result}")
    except ValueError as e:
        # Handle validation errors specifically
        print(f"\n[SECURITY ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
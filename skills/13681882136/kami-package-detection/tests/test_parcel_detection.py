"""
parcel-detection-skill-new unit tests

Validates requirements: 1.1, 1.2, 1.6, 1.7, 1.8, 1.9
"""
import os
import sys
import json
import types
import pytest
import yaml
import subprocess
from unittest.mock import patch, MagicMock

# Path setup
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(SKILL_DIR, ".."))
sys.path.insert(0, SKILL_DIR)

SKILL_MD_PATH = os.path.join(SKILL_DIR, "SKILL.md")
REQUIREMENTS_PATH = os.path.join(SKILL_DIR, "requirements.txt")
SCRIPT_PATH = os.path.join(SKILL_DIR, "yolo_world_onnx.py")


def _import_yolo_module():
    """Import yolo_world_onnx module, mocking heavy dependencies if missing."""
    saved = {}
    mock_modules = ["cv2", "numpy", "onnxruntime"]
    for mod_name in mock_modules:
        if mod_name in sys.modules:
            saved[mod_name] = sys.modules[mod_name]

    for mod_name in mock_modules:
        if mod_name not in sys.modules:
            mock_mod = MagicMock()
            if mod_name == "numpy":
                mock_mod.ndarray = MagicMock
                mock_mod.copy = MagicMock()
                mock_mod.array = MagicMock()
                mock_mod.expand_dims = MagicMock()
                mock_mod.ascontiguousarray = MagicMock()
                mock_mod.clip = MagicMock()
                mock_mod.max = MagicMock()
                mock_mod.argmax = MagicMock()
            sys.modules[mod_name] = mock_mod

    if "yolo_world_onnx" in sys.modules:
        del sys.modules["yolo_world_onnx"]

    import yolo_world_onnx
    return yolo_world_onnx


def parse_skill_md_frontmatter(path: str) -> dict:
    """Parse SKILL.md YAML frontmatter (content between --- delimiters)."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing YAML frontmatter start marker '---'")
    end_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break
    if end_index is None:
        raise ValueError("SKILL.md missing YAML frontmatter end marker '---'")
    frontmatter_text = "\n".join(lines[1:end_index])
    return yaml.safe_load(frontmatter_text)


# ===========================================================================
# 1. Directory Structure Validation (Requirement 1.1)
# ===========================================================================

class TestDirectoryStructure:
    """Verify parcel-detection-skill-new/ directory exists with required files."""

    def test_skill_directory_exists(self):
        assert os.path.isdir(SKILL_DIR), f"Directory not found: {SKILL_DIR}"

    @pytest.mark.parametrize("filename", [
        ".gitignore",
        "requirements.txt",
        "yolo_world_onnx.py",
        "SKILL.md",
        "setup.sh",
    ])
    def test_required_file_exists(self, filename):
        filepath = os.path.join(SKILL_DIR, filename)
        assert os.path.isfile(filepath), f"Required file missing: {filename}"


# ===========================================================================
# 2. requirements.txt Content Validation (Requirement 1.8)
# ===========================================================================

class TestRequirements:
    """Verify requirements.txt contains correct dependencies."""

    def setup_method(self):
        with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
            self.content = f.read()
        self.lines = [
            line.strip().lower()
            for line in self.content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    def test_contains_onnxruntime(self):
        assert any("onnxruntime" in line for line in self.lines)

    def test_contains_opencv(self):
        assert any("opencv-python-headless" in line for line in self.lines)

    def test_contains_numpy(self):
        assert any("numpy" in line for line in self.lines)

    def test_does_not_contain_edge_tts(self):
        assert not any("edge-tts" in line for line in self.lines), \
            "requirements.txt should not contain edge-tts"


# ===========================================================================
# 3. Command-Line Argument Validation (Requirement 1.9, 1.10)
# ===========================================================================

class TestCommandLineArgs:
    """Verify yolo_world_onnx.py command-line arguments."""

    def setup_method(self):
        mod = _import_yolo_module()
        self.parse_args = mod.parse_args

    def test_accepts_rtsp_url(self):
        with patch("sys.argv", ["yolo_world_onnx.py", "--rtsp_url", "rtsp://test"]):
            args = self.parse_args()
        assert args.rtsp_url == "rtsp://test"

    def test_accepts_conf_threshold(self):
        with patch("sys.argv", ["yolo_world_onnx.py", "--conf_threshold", "0.5"]):
            args = self.parse_args()
        assert args.conf_threshold == 0.5

    def test_accepts_class_names(self):
        with patch("sys.argv", ["yolo_world_onnx.py", "--class_names", "parcel", "box"]):
            args = self.parse_args()
        assert args.class_names == ["parcel", "box"]

    def test_accepts_run_time(self):
        with patch("sys.argv", ["yolo_world_onnx.py", "--run_time", "120"]):
            args = self.parse_args()
        assert args.run_time == 120

    def test_no_device_id_arg(self):
        """Verify --device_id argument is not present."""
        with patch("sys.argv", ["yolo_world_onnx.py"]):
            args = self.parse_args()
        assert not hasattr(args, "device_id"), "Should not have --device_id argument"

    def test_no_detect_text_arg(self):
        """Verify --detect_text argument is not present."""
        with patch("sys.argv", ["yolo_world_onnx.py"]):
            args = self.parse_args()
        assert not hasattr(args, "detect_text"), "Should not have --detect_text argument"


# ===========================================================================
# 4. SKILL.md Frontmatter Validation (Requirement 1.1)
# ===========================================================================

class TestSkillMdFrontmatter:
    """Verify SKILL.md YAML frontmatter."""

    def setup_method(self):
        self.frontmatter = parse_skill_md_frontmatter(SKILL_MD_PATH)

    def test_name_is_correct(self):
        assert self.frontmatter["name"] == "kami-package-detection"

    def test_description_non_empty(self):
        assert self.frontmatter.get("description"), "description field must not be empty"

    def test_metadata_bins_contains_python3(self):
        bins = self.frontmatter["metadata"]["openclaw"]["requires"]["bins"]
        assert "python3" in bins, f"bins should contain python3, got: {bins}"


# ===========================================================================
# 5. Error Handling Edge Cases (Requirement 1.6, 1.7)
# ===========================================================================

class TestErrorHandling:
    """Verify error handling: model file not found and RTSP connection failure."""

    def test_model_file_not_found_exits_nonzero(self):
        """Should exit with non-zero code when model file is missing."""
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH,
             "--rtsp_url", "rtsp://127.0.0.1/nonexistent",
             "--run_time", "5"],
            capture_output=True, text=True, timeout=15,
            cwd=SKILL_DIR,
            env={**os.environ, "PYTHONPATH": SKILL_DIR},
        )
        assert result.returncode != 0, \
            f"Should return non-zero exit code when model file missing, got: {result.returncode}"

    def test_rtsp_connection_failure_exits_nonzero(self):
        """Should exit with non-zero code when RTSP connection fails."""
        fake_model = os.path.join(SKILL_DIR, "yolov8s-worldv2.onnx")
        model_existed = os.path.exists(fake_model)
        if not model_existed:
            with open(fake_model, "wb") as f:
                f.write(b"\x00" * 10)
        try:
            result = subprocess.run(
                [sys.executable, SCRIPT_PATH,
                 "--rtsp_url", "rtsp://192.0.2.1/nonexistent",
                 "--run_time", "5"],
                capture_output=True, text=True, timeout=30,
                cwd=SKILL_DIR,
                env={**os.environ, "PYTHONPATH": SKILL_DIR},
            )
            assert result.returncode != 0, \
                f"Should return non-zero exit code on RTSP failure, got: {result.returncode}"
        finally:
            if not model_existed and os.path.exists(fake_model):
                os.remove(fake_model)


# ===========================================================================
# 6. format_detection_result Validation (Requirement 1.4)
# ===========================================================================

class TestFormatDetectionResult:
    """Verify format_detection_result returns correct dict structure."""

    def setup_method(self):
        mod = _import_yolo_module()
        self.format_detection_result = mod.format_detection_result

    def test_returns_dict_with_correct_keys(self):
        result = self.format_detection_result("parcel", [100, 200, 300, 400])
        assert isinstance(result, dict)
        assert "class_name" in result
        assert "bbox" in result

    def test_bbox_has_correct_keys(self):
        result = self.format_detection_result("parcel", [100, 200, 300, 400])
        bbox = result["bbox"]
        assert "x1" in bbox
        assert "y1" in bbox
        assert "x2" in bbox
        assert "y2" in bbox

    def test_values_are_correct(self):
        result = self.format_detection_result("box", [10, 20, 30, 40])
        assert result["class_name"] == "box"
        assert result["bbox"] == {"x1": 10, "y1": 20, "x2": 30, "y2": 40}

    def test_result_is_json_serializable(self):
        result = self.format_detection_result("parcel", [0, 0, 100, 100])
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        assert parsed == result


# ===========================================================================
# 7. No TTS Code Validation (Requirement 1.3, 1.10)
# ===========================================================================

class TestNoTTSCode:
    """Verify yolo_world_onnx.py contains no TTS-related code."""

    def setup_method(self):
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_no_edge_tts_import(self):
        assert "edge_tts" not in self.content, "Should not contain edge_tts"

    def test_no_tts_manager(self):
        assert "TTSManager" not in self.content, "Should not contain TTSManager"

    def test_no_device_id_arg(self):
        assert "--device_id" not in self.content, "Should not contain --device_id"

    def test_no_detect_text_arg(self):
        assert "--detect_text" not in self.content, "Should not contain --detect_text"

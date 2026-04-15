#!/usr/bin/env python3
"""
xhs-anti-detection Skill 测试套件
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np
from PIL import Image

# 添加技能目录到路径
import sys
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))

from scripts.clean_metadata import clean_metadata
from scripts.add_noise import add_noise
from scripts.color_shift import color_shift
from scripts.recompress import recompress
from scripts.verify import verify_image
from scripts.process import process_image as process_single

class TestMetadataCleaner(unittest.TestCase):
    """测试元数据清理"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_img = self.temp_dir / "input.png"
        self.output_img = self.temp_dir / "output.png"

        # 创建测试图片
        img = Image.new("RGB", (100, 100), color="red")
        img.save(self.input_img)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_clean_metadata(self):
        """测试元数据清理"""
        # 添加测试元数据
        import subprocess
        subprocess.run([
            "exiftool", "-overwrite_original",
            f"-Software=TestAI",
            f"-Creator=TestBot",
            str(self.input_img)
        ], capture_output=True)

        # 执行清理
        clean_metadata(self.input_img, self.output_img, "medium", verbose=False)

        # 验证输出文件存在
        self.assertTrue(self.output_img.exists())

        # 验证元数据已清除
        result = subprocess.run(
            ["exiftool", "-Software", "-Creator", "-json", str(self.output_img)],
            capture_output=True, text=True
        )
        # 应该没有 Software 和 Creator 字段（或为空）
        self.assertNotIn("TestAI", result.stdout)

class TestNoiseAdder(unittest.TestCase):
    """测试噪声添加"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_img = self.temp_dir / "input.png"
        self.output_img = self.temp_dir / "output.png"

        # 创建纯色测试图片
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        img.save(self.input_img)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_add_noise_changes_pixels(self):
        """测试噪声确实改变了像素"""
        add_noise(self.input_img, self.output_img, "medium", verbose=False)

        orig = np.array(Image.open(self.input_img))
        noisy = np.array(Image.open(self.output_img))

        # 图片应该不同（噪声添加）
        self.assertFalse(np.array_equal(orig, noisy))

    def test_noise_levels(self):
        """测试不同级别的噪声强度"""
        outputs = []
        for level in ["light", "medium", "heavy"]:
            out = self.temp_dir / f"out_{level}.png"
            add_noise(self.input_img, out, level, verbose=False)
            outputs.append(out)

        # 计算差异
        diffs = []
        for out in outputs:
            orig = np.array(Image.open(self.input_img))
            noisy = np.array(Image.open(out))
            diffs.append(np.mean(np.abs(noisy.astype(float) - orig.astype(float))))

        # heavy 应该比 light 差异更大
        self.assertGreater(diffs[2], diffs[0])

class TestColorShifter(unittest.TestCase):
    """测试色彩偏移"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_img = self.temp_dir / "input.png"
        self.output_img = self.temp_dir / "output.png"

        img = Image.new("RGB", (100, 100), color=(255, 0, 0))  # 红色
        img.save(self.input_img)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_color_shift_changes_color(self):
        """测试色彩偏移改变了颜色"""
        color_shift(self.input_img, self.output_img, "medium", verbose=False)

        orig = np.array(Image.open(self.input_img))
        shifted = np.array(Image.open(self.output_img))

        # 红色应该变化（不再是纯红）
        self.assertFalse(np.array_equal(orig, shifted))

class TestRecompressor(unittest.TestCase):
    """测试重新编码"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_img = self.temp_dir / "input.png"
        self.output_img = self.temp_dir / "output.jpg"

        img = Image.new("RGB", (100, 100), color="blue")
        img.save(self.input_img)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_recompress_to_jpg(self):
        """测试输出为 JPG 格式"""
        recompress(self.input_img, self.output_img, "medium", verbose=False)
        self.assertTrue(self.output_img.exists())
        self.assertEqual(self.output_img.suffix.lower(), ".jpg")

    def test_quality_high(self):
        """测试高质量保存"""
        recompress(self.input_img, self.output_img, "medium", verbose=False)
        img = Image.open(self.output_img)
        # 质量 97 应该接近原图
        orig = np.array(Image.open(self.input_img))
        compressed = np.array(img)
        # PSNR 应该 > 30dB（粗略估计）
        mse = np.mean((orig.astype(float) - compressed.astype(float)) ** 2)
        psnr = 10 * np.log10(255**2 / (mse + 1e-8))
        self.assertGreater(psnr, 30)

class TestVerifier(unittest.TestCase):
    """测试验证器"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        # 创建一个处理后图片
        self.test_img = self.temp_dir / "test.jpg"
        img = Image.new("RGB", (200, 200), color="green")
        img.save(self.test_img)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_verify_returns_dict(self):
        """测试验证返回正确结构"""
        result = verify_image(self.test_img, "medium")

        self.assertIn("checks", result)
        self.assertIn("quality", result)
        self.assertIn("risk", result)

        # 检查必须字段
        for check in ["metadata_clean", "text_clear", "noise_adequate", "color_natural"]:
            self.assertIn(check, result["checks"])

class TestFullPipeline(unittest.TestCase):
    """测试完整流水线"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_img = self.temp_dir / "input.png"
        self.output_img = self.temp_dir / "output.png"

        img = Image.new("RGB", (200, 200), color=(100, 150, 200))
        img.save(self.input_img)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_full_pipeline(self):
        """测试完整处理流程"""
        from scripts.process import process_single

        success = process_single(
            input_path=self.input_img,
            output_path=self.output_img,
            level="medium",
            verbose=False,
            skip_verify=True  # 跳过验证以加速测试
        )

        self.assertTrue(success)
        self.assertTrue(self.output_img.exists())

def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestMetadataCleaner))
    suite.addTests(loader.loadTestsFromTestCase(TestNoiseAdder))
    suite.addTests(loader.loadTestsFromTestCase(TestColorShifter))
    suite.addTests(loader.loadTestsFromTestCase(TestRecompressor))
    suite.addTests(loader.loadTestsFromTestCase(TestVerifier))
    suite.addTests(loader.loadTestsFromTestCase(TestFullPipeline))

    # 运行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

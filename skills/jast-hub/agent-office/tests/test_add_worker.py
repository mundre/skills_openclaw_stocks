import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "add_worker.py"
SPEC = importlib.util.spec_from_file_location("add_worker_module", MODULE_PATH)
add_worker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(add_worker)


class AddWorkerTests(unittest.TestCase):
    def test_pinyin_uses_expected_worker_id(self):
        self.assertEqual(add_worker.pinyin("小龙"), "xiaolong")
        self.assertEqual(add_worker.pinyin("小D"), "xiaod")

    def test_cli_profile_display_uses_builtin_catalog(self):
        self.assertEqual(add_worker.cli_profile_display("codex"), "OpenAI Codex CLI")
        self.assertEqual(add_worker.cli_profile_display("claude-code"), "Claude Code")

    def test_render_template_replaces_known_tokens(self):
        rendered = add_worker.render_template(
            "Hello {{NAME}} on {{PORT}}",
            {"NAME": "小龙", "PORT": 5011},
        )
        self.assertEqual(rendered, "Hello 小龙 on 5011")

    def test_write_soul_renders_engine_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            worker_dir = Path(tmpdir)
            add_worker.write_soul(
                worker_dir=worker_dir,
                name="小龙",
                worker_id="xiaolong",
                role="research",
                engine="openclaw",
                port=5011,
            )
            content = (worker_dir / "SOUL.md").read_text(encoding="utf-8")
            self.assertIn("员工编号：xiaolong", content)
            self.assertIn("运行端口：5011", content)
            self.assertIn("竞品调研、信息收集、事实核查与资料整理", content)

    def test_write_soul_renders_cli_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            worker_dir = Path(tmpdir)
            add_worker.write_soul(
                worker_dir=worker_dir,
                name="小克",
                worker_id="xiaoke",
                role="code",
                engine="cli",
                port=5016,
                cli_profile="claude-code",
            )
            content = (worker_dir / "SOUL.md").read_text(encoding="utf-8")
            self.assertIn("Claude Code", content)
            self.assertIn("xiaoke", content)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.config import load_frontier_env  # noqa: E402
from frontier_search import cli  # noqa: E402


class ConfigTests(unittest.TestCase):
    def test_loads_private_dotenv_without_shell_expansion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            env_file = home / ".env"
            env_file.write_text(
                "# comments\n"
                "export X_BEARER_TOKEN=from-file\n"
                "OPENALEX_EMAIL='research@example.com'\n"
                "UNSUPPORTED_SECRET=should-not-load\n"
                "SEMANTIC_SCHOLAR_API_KEY=$(touch should-not-exist)\n",
                encoding="utf-8",
            )
            env_file.chmod(0o600)
            with patch.dict(os.environ, {"FRONTIER_HOME": str(home)}, clear=False):
                for key in (
                    "X_BEARER_TOKEN",
                    "OPENALEX_EMAIL",
                    "SEMANTIC_SCHOLAR_API_KEY",
                    "UNSUPPORTED_SECRET",
                ):
                    os.environ.pop(key, None)
                loaded = load_frontier_env()
                self.assertEqual(set(loaded), {"X_BEARER_TOKEN", "OPENALEX_EMAIL"})
                self.assertEqual(os.environ["X_BEARER_TOKEN"], "from-file")
                self.assertEqual(os.environ["OPENALEX_EMAIL"], "research@example.com")
                self.assertNotIn("UNSUPPORTED_SECRET", os.environ)

            self.assertFalse((home / "should-not-exist").exists())

    def test_existing_environment_wins_over_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            env_file = home / ".env"
            env_file.write_text("X_BEARER_TOKEN=from-file\n", encoding="utf-8")
            env_file.chmod(0o600)
            with patch.dict(
                os.environ,
                {"FRONTIER_HOME": str(home), "X_BEARER_TOKEN": "from-env"},
            ):
                self.assertEqual(load_frontier_env(), ())
                self.assertEqual(os.environ["X_BEARER_TOKEN"], "from-env")

    def test_warns_for_weak_permissions_without_revealing_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            path = home / ".env"
            path.write_text("X_BEARER_TOKEN=do-not-print\n", encoding="utf-8")
            path.chmod(0o644)
            output = io.StringIO()
            with patch.dict(os.environ, {"FRONTIER_HOME": str(home)}, clear=False):
                os.environ.pop("X_BEARER_TOKEN", None)
                with contextlib.redirect_stderr(output):
                    load_frontier_env()

            self.assertIn("chmod 600", output.getvalue())
            self.assertNotIn("do-not-print", output.getvalue())

    @patch("frontier_search.cli.run_search")
    @patch("frontier_search.cli.XRecentAdapter.is_configured")
    def test_cli_loads_before_provider_configuration_check(
        self, is_configured, run_search
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            env_file = home / ".env"
            env_file.write_text("X_BEARER_TOKEN=from-file\n", encoding="utf-8")
            env_file.chmod(0o600)
            is_configured.side_effect = lambda: os.environ.get("X_BEARER_TOKEN") == "from-file"
            run_search.return_value.to_dict.return_value = {"ok": True}
            output = io.StringIO()
            with patch.dict(os.environ, {"FRONTIER_HOME": str(home)}, clear=False):
                os.environ.pop("X_BEARER_TOKEN", None)
                with contextlib.redirect_stdout(output):
                    self.assertEqual(cli.main(["--query", "agents", "--x"]), 0)

            is_configured.assert_called_once_with()
            run_search.assert_called_once()
            self.assertIn('"ok": true', output.getvalue())

    @patch("frontier_search.cli.run_search")
    @patch("frontier_search.cli.XRecentAdapter.is_configured", return_value=True)
    def test_configured_x_is_enabled_by_default(self, _configured, run_search) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            env_file = home / ".env"
            env_file.write_text("X_BEARER_TOKEN=from-file\n", encoding="utf-8")
            env_file.chmod(0o600)
            run_search.return_value.to_dict.return_value = {"ok": True}
            with patch.dict(os.environ, {"FRONTIER_HOME": str(home)}, clear=False):
                os.environ.pop("X_BEARER_TOKEN", None)
                with contextlib.redirect_stdout(io.StringIO()):
                    cli.main(["--query", "agents"])

        request = run_search.call_args.args[0]
        self.assertTrue(request.x_enabled)

    @patch("frontier_search.cli.run_search")
    @patch("frontier_search.cli.XRecentAdapter.is_configured", return_value=True)
    def test_frontier_x_enabled_false_opts_out(self, _configured, run_search) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            env_file = home / ".env"
            env_file.write_text(
                "X_BEARER_TOKEN=from-file\nFRONTIER_X_ENABLED=false\n",
                encoding="utf-8",
            )
            env_file.chmod(0o600)
            run_search.return_value.to_dict.return_value = {"ok": True}
            with patch.dict(os.environ, {"FRONTIER_HOME": str(home)}, clear=False):
                os.environ.pop("X_BEARER_TOKEN", None)
                os.environ.pop("FRONTIER_X_ENABLED", None)
                with contextlib.redirect_stdout(io.StringIO()):
                    cli.main(["--query", "agents"])

        request = run_search.call_args.args[0]
        self.assertFalse(request.x_enabled)

    def test_missing_file_is_quiet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"FRONTIER_HOME": directory}, clear=False):
                self.assertEqual(load_frontier_env(), ())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from subprocess import run
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import install  # noqa: E402


class InstallerTests(unittest.TestCase):
    def test_curl_bootstrap_has_valid_shell_syntax(self) -> None:
        result = run(["sh", "-n", str(ROOT / "scripts" / "install.sh")], check=False)
        self.assertEqual(result.returncode, 0)

    def test_curl_bootstrap_installs_from_local_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            archive = base / "frontier-main.tar.gz"
            with tarfile.open(archive, "w:gz") as output:
                for relative in ("scripts/install.py", "skills/frontier/SKILL.md"):
                    path = ROOT / relative
                    output.add(path, arcname=f"frontier-main/{relative}")

            home = base / "home"
            environment = os.environ.copy()
            environment.update(
                {
                    "HOME": str(home),
                    "FRONTIER_ARCHIVE_URL": archive.as_uri(),
                    "TMPDIR": str(base),
                }
            )
            result = run(
                ["sh", str(ROOT / "scripts" / "install.sh"), "--agent", "claude"],
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((home / ".claude" / "skills" / "frontier" / "SKILL.md").is_file())

    def test_installs_and_uninstalls_to_runtime_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            destinations = {
                "claude": base / "claude" / "frontier",
                "codex": base / "agents" / "frontier",
                "opencode": base / "agents" / "frontier",
            }
            with patch.object(install, "AGENT_DESTINATIONS", destinations):
                self.assertEqual(install.install(["claude"], dry_run=False), 0)
                self.assertTrue((destinations["claude"] / "SKILL.md").is_file())
                stale_file = destinations["claude"] / "stale.txt"
                stale_file.write_text("stale installation content")
                self.assertEqual(install.install(["claude"], dry_run=False), 0)
                self.assertFalse(stale_file.exists())
                self.assertTrue((destinations["claude"] / "SKILL.md").is_file())
                self.assertEqual(install.install(["claude"], force=True), 0)
                self.assertEqual(install.uninstall(["claude"]), 0)
                self.assertFalse(destinations["claude"].exists())

    def test_all_deduplicates_shared_codex_opencode_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            shared = Path(directory) / "shared"
            destinations = {
                "claude": Path(directory) / "claude",
                "codex": shared,
                "opencode": shared,
            }
            with patch.object(install, "AGENT_DESTINATIONS", destinations):
                self.assertEqual(len(install.destinations(["claude", "codex", "opencode"])), 2)


if __name__ == "__main__":
    unittest.main()

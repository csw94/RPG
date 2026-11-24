"""Release tooling: notes come from HANDOVER, and CI runs the tests before building."""

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import release_notes  # noqa: E402


class ReleaseNotesTests(unittest.TestCase):
    def test_notes_quote_the_handover_entry(self):
        text = "## 릴리즈 기록\n- **v9.9.9:** 무언가 멋진 변경\n- **v9.9.8:** 이전 변경\n"
        notes = release_notes.notes_for("v9.9.9", text)
        self.assertIn("무언가 멋진 변경", notes)
        self.assertNotIn("이전 변경", notes)
        self.assertIn("ChroniclesOfPixel.exe", notes)

    def test_unknown_tag_falls_back(self):
        self.assertEqual(release_notes.notes_for("v0.0.0", "nothing"), release_notes.FALLBACK)

    def test_dots_in_tags_are_literal(self):
        self.assertEqual(release_notes.notes_for("v1.2.3", "- **v1x2x3:** wrong\n"), release_notes.FALLBACK)

    def test_current_release_has_notes(self):
        handover = (ROOT / "HANDOVER.md").read_text(encoding="utf-8")
        latest = handover.split("최신 릴리즈:** ")[1].split(" ")[0]
        self.assertNotEqual(release_notes.notes_for(latest, handover), release_notes.FALLBACK)


class WorkflowTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")

    def test_release_runs_tests_before_building(self):
        release = self.read("release.yml")
        self.assertIn("unittest discover -s tests", release)
        self.assertLess(release.index("unittest discover"), release.index("pyinstaller"))
        self.assertIn("release_notes.py", release)

    def test_ci_tests_every_push_to_main(self):
        ci = self.read("ci.yml")
        self.assertIn("branches: [main]", ci)
        self.assertIn("unittest discover -s tests", ci)

    def test_ci_uses_the_local_python_version(self):
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        for name in ("ci.yml", "release.yml"):
            self.assertIn(f'python-version: "{version}"', self.read(name), name)


if __name__ == "__main__":
    unittest.main()

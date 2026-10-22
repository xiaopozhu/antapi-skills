import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import check_structure


class StructureTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "skills").mkdir()

    def check(self, required=False):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = check_structure.check(self.root, require_skills=required)
        return code, output.getvalue()

    def test_empty_bootstrap_is_explicit(self):
        code, output = self.check()
        self.assertEqual(code, 0)
        self.assertIn("0 skills", output)
        self.assertIn("nothing installable", output)

    def test_release_rejects_empty_repository(self):
        code, _ = self.check(required=True)
        self.assertEqual(code, 1)

    def test_skill_requires_nonempty_entrypoint(self):
        folder = self.root / "skills" / "antapi-whois"
        folder.mkdir()
        self.assertEqual(self.check()[0], 1)
        (folder / "SKILL.md").write_text("", encoding="utf-8")
        self.assertEqual(self.check()[0], 1)
        (folder / "SKILL.md").write_text("---\nname: antapi-whois\ndescription: Domain lookup\n---\nInstructions\n", encoding="utf-8")
        self.assertEqual(self.check(required=True)[0], 0)

    def test_symlink_is_rejected(self):
        folder = self.root / "skills" / "antapi-whois"
        folder.mkdir()
        (folder / "SKILL.md").symlink_to(self.root / "outside.md")
        self.assertEqual(self.check()[0], 1)

    def test_invalid_skill_directory_is_rejected(self):
        folder = self.root / "skills" / "Invalid_Name"
        folder.mkdir()
        (folder / "SKILL.md").write_text("instructions", encoding="utf-8")
        self.assertEqual(self.check()[0], 1)


if __name__ == "__main__":
    unittest.main()

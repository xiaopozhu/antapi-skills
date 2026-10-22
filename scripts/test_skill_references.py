"""验证引用只依赖单个 Skill 内的真实文件。"""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import check_structure


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skills" / "antapi-whois"
        self.skill.mkdir(parents=True)

    def check(self, content):
        (self.skill / "SKILL.md").write_text(content, encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return check_structure.check(self.root)

    def test_missing_local_file_rejected(self):
        self.assertEqual(self.check("[missing](references/missing.md)"), 1)

    def test_existing_local_file_and_external_links_allowed(self):
        (self.skill / "reference.md").write_text("ok")
        self.assertEqual(self.check("[local](reference.md#section) [web](https://example.com)"), 0)

    def test_escaping_relative_links_rejected_even_if_target_exists(self):
        (self.root / "outside.md").write_text("outside")
        for target in ("../../outside.md", "%2e%2e/%2e%2e/outside.md",
                       str(self.root / "outside.md"), "file:///tmp/outside.md"):
            with self.subTest(target=target):
                self.assertEqual(self.check(f"[outside]({target})"), 1)

    def test_cross_skill_dependency_rejected(self):
        other = self.root / "skills" / "antapi-other"
        other.mkdir()
        (other / "SKILL.md").write_text("other")
        self.assertEqual(self.check("[other](../antapi-other/SKILL.md)"), 1)

    def test_reference_definition_and_html_links_checked(self):
        for content in ("[guide][id]\n\n[id]: missing.md", '<a href="../outside.md">link</a>'):
            with self.subTest(content=content):
                self.assertEqual(self.check(content), 1)

    def test_markdown_in_reference_checked_independently(self):
        (self.skill / "reference.md").write_text("[outside](../outside.md)")
        self.assertEqual(self.check("[reference](reference.md)"), 1)


if __name__ == "__main__":
    unittest.main()

"""验证分发包可复现，并拒绝越界路径和不安全文件。"""

import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest

import package_skills
from check_structure import skill_files


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skills" / "antapi-whois"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(
            "---\nname: antapi-whois\ndescription: WHOIS lookup\n---\n"
            "See [CLI](references/cli.md).\n", encoding="utf-8")
        (self.skill / "references").mkdir()
        (self.skill / "references" / "cli.md").write_text("CLI\n", encoding="utf-8")

    def package(self, output="out"):
        return package_skills.package(self.root, self.root / output, "0.1.0", "uncommitted")

    def test_deterministic_content_and_checksums(self):
        first = self.package("one")
        (self.skill / "SKILL.md").chmod(0o755)
        second = self.package("two")
        self.assertEqual(first, second)
        archive = "antapi-whois-0.1.0.tar.gz"
        one, two = self.root / "one", self.root / "two"
        self.assertEqual((one / archive).read_bytes(), (two / archive).read_bytes())
        digest = hashlib.sha256((one / archive).read_bytes()).hexdigest()
        self.assertIn(f"{digest}  {archive}\n", (one / "SHA256SUMS").read_text())
        manifest = json.loads((one / "manifest.json").read_text())
        self.assertEqual(manifest["source_commit"], "uncommitted")
        self.assertEqual(manifest["packages"][0]["sha256"], digest)
        with tarfile.open(one / archive) as tar:
            self.assertEqual(tar.getnames(), [
                "antapi-whois/SKILL.md", "antapi-whois/references/cli.md"])
            self.assertTrue(all(item.isfile() and item.uid == 0 and item.mtime == 0 for item in tar))
            self.assertEqual(tar.extractfile("antapi-whois/SKILL.md").read(),
                             (self.skill / "SKILL.md").read_bytes())

    def test_empty_skills_rejected(self):
        empty = self.root / "empty"
        (empty / "skills").mkdir(parents=True)
        with self.assertRaises(ValueError):
            package_skills.package(empty, self.root / "out", "0.1.0", "uncommitted")

    def test_symlink_rejected(self):
        (self.skill / "linked").symlink_to(self.root)
        with self.assertRaises(ValueError):
            self.package()

    def test_output_inside_skill_rejected(self):
        with self.assertRaises(ValueError):
            package_skills.package(self.root, self.skill / "output", "0.1.0", "uncommitted")

    def test_path_metadata_rejected(self):
        for version in ("../escape", "0.1.0/escape", "", "v0.1.0"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                package_skills.package(self.root, self.root / "out", version, "uncommitted")
        with self.assertRaises(ValueError):
            package_skills.package(self.root, self.root / "out", "0.1.0", "../escape")

    def test_special_file_rejected(self):
        import os
        os.mkfifo(self.skill / "pipe")
        with self.assertRaises(ValueError):
            self.package()

    def test_local_directory_install_remains_independent(self):
        destination = self.root / "agent-home" / "skills" / self.skill.name
        shutil.copytree(self.skill, destination)
        self.skill.rename(self.root / "source-hidden")
        self.assertEqual(len(skill_files(destination)), 2)

    def test_fixed_archive_install_remains_independent(self):
        self.package()
        archive = self.root / "out" / "antapi-whois-0.1.0.tar.gz"
        destination = self.root / "archive-home" / "skills"
        with tarfile.open(archive) as tar:
            for member in tar:
                path = Path(member.name)
                self.assertTrue(member.isfile())
                self.assertEqual(path.parts[0], "antapi-whois")
                self.assertFalse(path.is_absolute())
                self.assertNotIn("..", path.parts)
                target = destination / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())
        self.skill.rename(self.root / "source-hidden")
        self.assertEqual(len(skill_files(destination / "antapi-whois")), 2)

    def test_skill_directory_symlink_cannot_package_outside_directory(self):
        self.skill.rename(self.root / "outside-skill")
        self.skill.symlink_to(self.root / "outside-skill", target_is_directory=True)
        with self.assertRaises(ValueError):
            self.package()


if __name__ == "__main__":
    unittest.main()

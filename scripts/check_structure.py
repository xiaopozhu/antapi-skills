"""检查可独立分发的 Skill 目录结构；不替代 Agent Skills 格式校验或行为验收。"""

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


def within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def skill_files(folder: Path):
    """只接受单个可独立分发目录内的普通文件。"""
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Skill must be a regular directory")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", folder.name) or len(folder.name) > 64:
        raise ValueError("Invalid skill directory")
    files = []
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError("Skill packages must not contain symlinks")
        if not within(path.resolve(), folder.resolve()):
            raise ValueError("Skill file escapes its directory")
        relative = path.relative_to(folder)
        if any(part in (".", "..") or "\\" in part for part in relative.parts):
            raise ValueError("Unsafe Skill file path")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ValueError("Skill packages may contain only regular files and directories")
    entrypoint = folder / "SKILL.md"
    if entrypoint not in files:
        raise ValueError("Every skill must contain SKILL.md")
    try:
        if not entrypoint.read_text(encoding="utf-8").strip():
            raise ValueError("SKILL.md must not be empty")
        for path in files:
            if path.suffix.lower() == ".md":
                check_links(folder, path)
    except UnicodeError as error:
        raise ValueError("Skill Markdown must be readable UTF-8") from error
    return files


def check_links(folder: Path, document: Path):
    """检查 Markdown 行内、引用定义与 HTML 链接；不抓取外部网页。"""
    content = document.read_text(encoding="utf-8")
    targets = re.findall(r"\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)", content)
    targets += re.findall(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", content)
    targets += re.findall(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", content, re.IGNORECASE)
    for target in targets:
        parsed = urlsplit(target.strip("<>"))
        if parsed.scheme in ("https", "http", "mailto"):
            continue
        if parsed.scheme or parsed.netloc:
            raise ValueError("Unsupported link scheme in Skill")
        decoded = unquote(parsed.path)
        if not decoded:
            continue
        if Path(decoded).is_absolute() or "\\" in decoded:
            raise ValueError("Local Skill links must be relative")
        resolved = (document.parent / decoded).resolve()
        if not within(resolved, folder.resolve()):
            raise ValueError("Local link escapes independent Skill directory")
        if not resolved.is_file():
            raise ValueError("Local Skill link must resolve to an existing file")


def skill_directories(root: Path):
    skills = root / "skills"
    if skills.is_symlink() or not skills.is_dir():
        raise ValueError("skills/ must be a regular directory")
    folders = []
    for folder in sorted(skills.iterdir()):
        if folder.name == ".gitkeep" and folder.is_file() and not folder.is_symlink():
            continue
        skill_files(folder)
        folders.append(folder)
    return folders


def check(root: Path, require_skills: bool = False) -> int:
    try:
        folders = skill_directories(root)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    count = len(folders)
    if not count:
        print("0 skills: repository bootstrap; nothing installable")
        return 1 if require_skills else 0
    print(f"{count} skills: structure and local references checked; format and behavior checks are still required")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-skills", action="store_true")
    args = parser.parse_args()
    return check(Path(__file__).resolve().parent.parent, args.require_skills)


if __name__ == "__main__":
    raise SystemExit(main())

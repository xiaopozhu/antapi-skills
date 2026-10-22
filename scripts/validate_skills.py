"""调用已安装的官方 skills-ref；结构检查不替代官方格式校验。"""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from check_structure import skill_directories


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validator", default="skills-ref")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        folders = skill_directories(root)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    if not folders:
        print("0 skills: bootstrap only; no official format validation performed")
        return 0
    validator = shutil.which(args.validator)
    if validator is None:
        print("Official skills-ref missing; install requirements-tools.txt in a virtual environment", file=sys.stderr)
        return 1
    for folder in folders:
        result = subprocess.run([validator, "validate", str(folder)], check=False)
        if result.returncode != 0:
            return result.returncode
    print(f"Official skills-ref validated {len(folders)} Skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

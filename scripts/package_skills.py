"""将每个独立 Skill 打包为可复现的 tar.gz，并输出校验和及真实来源元数据。"""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tarfile

from check_structure import skill_directories, skill_files, within


def package(root: Path, output: Path, version: str, commit: str):
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[a-zA-Z0-9.-]+)?", version):
        raise ValueError("version must be a safe SemVer without a v prefix")
    if commit != "uncommitted" and not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ValueError("commit must be a full SHA or uncommitted")
    folders = skill_directories(root)
    if not folders:
        raise ValueError("Cannot package an empty skills repository")
    if output.is_symlink() or within(output.resolve(), (root / "skills").resolve()):
        raise ValueError("Package output must be outside skills/ and not a symlink")
    # 在任何输出前完成全部输入校验，避免不完整包被误当成成功产物。
    sources = [(folder, skill_files(folder)) for folder in folders]
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"version": version, "source_commit": commit, "packages": []}
    for folder, files in sources:
        filename = f"{folder.name}-{version}.tar.gz"
        destination = output / filename
        if destination.is_symlink():
            raise ValueError("Archive output must not be a symlink")
        payload = io.BytesIO()
        with gzip.GzipFile(fileobj=payload, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
                for path in files:
                    data = path.read_bytes()
                    name = f"{folder.name}/{path.relative_to(folder).as_posix()}"
                    info = tarfile.TarInfo(name)
                    info.size, info.mode, info.mtime = len(data), 0o644, 0
                    archive.addfile(info, io.BytesIO(data))
        data = payload.getvalue()
        destination.write_bytes(data)
        manifest["packages"].append({"skill": folder.name, "archive": filename,
                                      "sha256": hashlib.sha256(data).hexdigest()})
    for name in ("manifest.json", "SHA256SUMS"):
        if (output / name).is_symlink():
            raise ValueError("Manifest output must not be a symlink")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "SHA256SUMS").write_text("".join(
        f"{entry['sha256']}  {entry['archive']}\n" for entry in manifest["packages"]), encoding="utf-8")
    return manifest


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", default=(root / "VERSION").read_text().strip())
    parser.add_argument("--commit", default="uncommitted")
    args = parser.parse_args()
    try:
        manifest = package(root, args.output, args.version, args.commit)
    except (OSError, ValueError, tarfile.TarError) as error:
        print(f"Packaging failed: {error}", file=sys.stderr)
        return 1
    print(f"Packaged {len(manifest['packages'])} independent Skill(s) into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

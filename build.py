"""
Builds the release Exordium downloads cores from: one zip per core folder, plus `cores.json` (the
catalog Exordium reads) and `SHA256SUMS.txt`, all into `dist/`.

    python build.py [tag]

Each zip holds one folder named for the core (`1.10f/Game.exe`, ...), as Exordium expects. Zips are
deterministic (sorted entries, fixed timestamps), so a core whose files did not change keeps the same
SHA-256 from release to release. With a tag, each catalog entry carries that release's download link,
so a catalog Exordium cached an hour ago still names zips that exist.
"""

import hashlib
import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
REPO = os.environ.get("GITHUB_REPOSITORY", "HarvestWombs/Exordium-Cores")
CORE = re.compile(r"^\d+\.\d+[a-z]?$", re.I)
# 1.14 and later are Blizzard's single Game.exe, which Exordium takes from the player's install.
SINGLE_EXE = re.compile(r"^1\.(1[4-9]|[2-9]\d)", re.I)
STAMP = (1980, 1, 1, 0, 0, 0)


def order(version):
    return re.sub(r"\d+", lambda m: m.group(0).zfill(3), version)


def zip_core(version, path):
    folder = os.path.join(ROOT, version)
    files = []
    for base, dirs, names in os.walk(folder):
        dirs.sort()
        for name in sorted(names):
            full = os.path.join(base, name)
            files.append((full, version + "/" + os.path.relpath(full, folder).replace(os.sep, "/")))
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for full, arcname in files:
            info = zipfile.ZipInfo(arcname, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(full, "rb") as f:
                archive.writestr(info, f.read())


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else None
    os.makedirs(DIST, exist_ok=True)
    versions = sorted(
        (v for v in os.listdir(ROOT)
         if CORE.match(v) and not SINGLE_EXE.match(v) and os.path.isdir(os.path.join(ROOT, v))),
        key=order,
    )
    cores = []
    for version in versions:
        file = version + ".zip"
        path = os.path.join(DIST, file)
        zip_core(version, path)
        entry = {"version": version, "core": version, "file": file, "size": os.path.getsize(path), "sha256": sha256(path)}
        if tag:
            entry["url"] = f"https://github.com/{REPO}/releases/download/{tag}/{file}"
        cores.append(entry)
        print(f"{file}: {entry['size']} bytes")
    with open(os.path.join(DIST, "cores.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"version": 1, "cores": cores}, indent=2) + "\n")
    with open(os.path.join(DIST, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.writelines(f"{c['sha256']}  {c['file']}\n" for c in cores)
    print(f"{len(cores)} cores in dist/")


if __name__ == "__main__":
    main()

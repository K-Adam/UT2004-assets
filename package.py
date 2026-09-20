"""Packages src/ into build/assets.tar.xz and one brotli file per content file plus files.json in build/web."""

import argparse
import hashlib
import json
import lzma
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
BUILD = ROOT / "build"
WEB = BUILD / "web"

# A dictionary this large lets the solid stream match across the many similar packages.
# Compression needs about 11x this in RAM.
DICT_SIZE = 512 << 20


def source_files():
    # Grouping by extension keeps packages of the same type adjacent in the solid stream.
    files = [p for p in SRC.rglob("*") if p.is_file()]
    return sorted(files, key=lambda p: (p.suffix.lower(), p.relative_to(SRC).as_posix().lower()))


def normalize(info):
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    return info


def build_archive():
    out = BUILD / "assets.tar.xz"
    part = out.with_name(out.name + ".part")
    filters = [{"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME, "dict_size": DICT_SIZE}]
    with lzma.open(part, "wb", filters=filters) as xz, tarfile.open(fileobj=xz, mode="w") as tar:
        for path in source_files():
            tar.add(path, arcname=path.relative_to(SRC).as_posix(), filter=normalize)
    part.replace(out)
    print(f"{out} {out.stat().st_size:,} bytes")


def build_file(path, previous):
    """Compresses one content file into web/ unless it is unchanged, and returns its manifest entry."""
    import brotli

    rel = path.relative_to(SRC).as_posix()
    data = path.read_bytes()
    entry = {"path": rel, "size": len(data), "hash": hashlib.sha256(data).hexdigest()[:16]}
    br = WEB / f"{rel}.br"
    if previous.get(rel) == entry["hash"] and br.exists():
        return entry
    # The files are served with Content-Encoding: br, lgwin 24 is the largest window browsers decode.
    br.parent.mkdir(parents=True, exist_ok=True)
    part = br.with_name(br.name + ".part")
    part.write_bytes(brotli.compress(data, quality=11, lgwin=24))
    part.replace(br)
    print(f"{rel} {br.stat().st_size:,} bytes")
    return entry


def build_web():
    WEB.mkdir(exist_ok=True)
    manifest = WEB / "files.json"
    previous = {}
    if manifest.exists():
        previous = {e["path"]: e["hash"] for e in json.loads(manifest.read_text(encoding="utf-8"))}
    # brotli releases the GIL, so threads compress in parallel. Eight keep quality 11 within a few GB of RAM.
    with ThreadPoolExecutor(8) as pool:
        entries = list(pool.map(lambda p: build_file(p, previous), source_files()))
    # Written last, so a manifest only ever lists files that are in place.
    manifest.write_text(json.dumps(entries), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", choices=["archive", "web", "all"], default="all")
    target = parser.parse_args().target
    BUILD.mkdir(exist_ok=True)
    if target in ("archive", "all"):
        build_archive()
    if target in ("web", "all"):
        build_web()


if __name__ == "__main__":
    main()

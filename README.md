# Unreal Tournament 2004 Modernized: development content

The content set the modernized port of Unreal Tournament 2004 (build 3369) is developed and tested with: ten DM, CTF and ONS maps, the menu maps and the packages they need. It is about 2.0 GB, kept in Git LFS. Every file is identical to retail, so the maps work on retail servers without downloads.

## Packaging

`python package.py` writes into `build/`:

- `assets.tar.xz`: all of `src/` in one archive, for the Android build. Compressing needs about 6 GB of RAM.
- `web/`: each file as `<path>.br` plus `files.json` with its path, size and hash, for the web build. Unchanged files are not compressed again. Needs `pip install -r requirements.txt`.

Pass `archive` or `web` to build only one. Both are hosted at `https://assets.ut2004.dev`, the `.br` files under their plain names with `Content-Encoding: br`.

## Ownership

All content in this repository is taken from a retail copy of the game and belongs to Epic Games, Inc. or their respective owners. This repository grants no license to it and is not affiliated with, endorsed by, or sponsored by Epic Games, Inc.

If you represent Epic Games and have any request or concern about this repository, including a request to take it down, please contact me at kecskes.adam@outlook.com. I will respond promptly and comply with any reasonable request.

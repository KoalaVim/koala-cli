#!/usr/bin/env python3

from pathlib import Path


def install_neovim(file: Path):
    print(f"install neovim {file}")


def install_nerdfont(file: Path):
    print(f"install nerdfont {file}")


def get_nerdfont() -> str:
    return "CascadiaCode.tar.xz"

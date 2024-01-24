#!/usr/bin/env python3

import glob
from pathlib import Path


# TODO: add arg to install in different basedir
# TODO: track installed files and dir to implement uninstall after
def install_dir(dir: Path):
    print(f'installing {dir}')


def install_dirs(dirs: Path):
    [install_dir(dir) for dir in dirs]


def install_neovim(out_dir: Path):
    install_dirs(glob.glob(str(out_dir / 'nvim-linux64' / "*")))


def install_nerdfont(out_dir: Path):
    print(f"install nerdfont {out_dir}")


def get_nerdfont() -> str:
    return "CascadiaCode.tar.xz"

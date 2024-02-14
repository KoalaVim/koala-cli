#!/usr/bin/env python3

import glob
from pathlib import Path
from typing import Callable, List

from rich.console import Console

from koala_cli.utils import base_bin_dir

Installer = Callable[[Console, Path], None]

# TODO: add arg to install in different basedir
# TODO: track installed files and dir to implement uninstall after
def install_dir(console: Console, dir: Path, base_dir: Path, output_dir: Path):
    console.print(
        f'Installing [bright_magenta]{dir.relative_to(base_dir)} [/bright_magenta]in [cyan]{output_dir}'
    )


def install_dirs(console: Console, dirs: List[str], base_dir: Path, output_dir: Path):
    [install_dir(console, Path(dir), base_dir, output_dir) for dir in dirs]


def install_neovim(console: Console, in_dir: Path):
    base_dir = Path(in_dir / 'nvim-linux64')
    install_dirs(console, glob.glob(str(base_dir / "*")), base_dir, base_bin_dir())


def install_nerdfont(console: Console, in_dir: Path):
    print(f"install nerdfont {in_dir}")


def get_nerdfont() -> str:
    return "CascadiaCode.tar.xz"

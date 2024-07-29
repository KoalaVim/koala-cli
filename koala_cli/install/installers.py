#!/usr/bin/env python3

import glob
from pathlib import Path
from typing import Callable, List

from rich.console import Console

from koala_cli.utils import base_bin_dir

Installer = Callable[[Console, Path], None]


# TODO: add arg to install in different basedir
# TODO: track installed files and dir to implement uninstall after
def install_path(console: Console, path: Path, base_dir: Path, output_dir: Path):
    console.print(
        f'Installing [bright_magenta]{path.relative_to(base_dir)} [/bright_magenta]in [cyan]{output_dir}'
    )


def install_paths(
    console: Console,
    paths: List[str],
    parent_dir: Path,
    output_dir: Path,
    debug=False,
):
    if len(paths) == 0:
        raise ValueError(f'no paths {parent_dir=}')
    if debug:
        print(f'{parent_dir=} {paths=}')
    [install_path(console, Path(dir), parent_dir, output_dir) for dir in paths]


def install_neovim(console: Console, parent_dir: Path):
    parent_dir = Path(parent_dir / 'nvim-linux64')
    install_paths(
        console,
        glob.glob(str(parent_dir / "*")),
        parent_dir,
        base_bin_dir(),
    )


def install_nerdfont(console: Console, parent_dir: Path):
    # TODO: impl
    print(f"install nerdfont {parent_dir}")


def get_nerdfont() -> str:
    return "CascadiaCode.tar.xz"


# TODO: [windows install] implement installers
def install_fd(console: Console, parent_dir: Path):
    install_paths(
        console,
        glob.glob(str(parent_dir / "fd-*" / "fd")),
        parent_dir,
        base_bin_dir() / 'bin',
    )


def install_ripgrep(console: Console, parent_dir: Path):
    install_paths(
        console,
        glob.glob(str(parent_dir / "ripgrep-*" / "rg")),
        parent_dir,
        base_bin_dir() / 'bin',
    )


def install_fzf(console: Console, parent_dir: Path):
    install_paths(
        console,
        [str(parent_dir / "fzf")],
        parent_dir,
        base_bin_dir() / 'bin',
    )

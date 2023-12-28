#!/usr/bin/env python3

import subprocess
import platform

from typing import Optional
import typer
from .dependencies import dependencies
from typing_extensions import Annotated
from typing import List

app = typer.Typer(help="Install KoalaVim and dependencies")


@app.callback(invoke_without_command=True)
def install(
    dry_run: bool = False,
    sudo: bool = True,
    as_binaries: Annotated[
        bool,
        typer.Option(
            help="Install dependencies as binaries rather via package manager"
        ),
    ] = False,
):
    if as_binaries:
        print("Not support yet, sorry :(")
        return typer.Exit(1)

    install_dependencies(dependencies, get_os_pkg_manger(), sudo, dry_run)


def install_dependencies(
    pkg_names: List[str], pkg_manager: str, sudo: bool, dry_run: bool
):
    args = []
    if sudo:
        args.append("sudo")

    args += [pkg_manager, "-y", *pkg_names]

    if dry_run:
        print(" ".join(args))
    # TODO: don't try to install neovim nerdfont from pkgmanager
    # subprocess.check_output()


def install_binary(name: str, sudo: bool, dry_run: bool, as_binary: bool):
    return


# None = unavailable pkg_manager
def get_os_pkg_manger() -> Optional[str]:
    system = platform.system()
    if system == "Linux":
        return get_linux_pkg_manager()
    elif system == "Darwin":
        return "brew"
    elif system == "Windows":
        return get_windows_pkg_manager()


def get_linux_pkg_manager() -> Optional[str]:
    manangers = ['apt', 'yum']
    for manager in manangers:
        if is_executable_available(manager):
            return manager

    return None


def get_windows_pkg_manager() -> Optional[str]:
    return None


def is_executable_available(executable: str) -> bool:
    try:
        subprocess.call([executable], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return False

    return True

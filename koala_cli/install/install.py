#!/usr/bin/env python3

import subprocess
import platform
import requests

from typing import Optional
import typer
from .dependencies import pkgs, binaries, overrides_by_os
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

    for binary in binaries:
        install_binary(binary, dry_run)

    install_pkgs(pkgs, get_os_pkg_manger(), sudo, dry_run)


def install_pkgs(pkg_names: List[str], pkg_manager: str, sudo: bool, dry_run: bool):
    args = []
    if sudo:
        args.append("sudo")

    args += [pkg_manager, "-y", *pkg_names]

    if dry_run:
        print(" ".join(args))
    # subprocess.check_output()


def install_binary(name: str, dry_run: bool):
    release = get_github_release(name)
    print(release)
    return


# None = unavailable pkg_manager
def get_os_pkg_manger() -> Optional[str]:
    system = _get_os()
    if system == "linux":
        return get_linux_pkg_manager()
    elif system == "mac":
        return "brew"
    elif system == "windows":
        return get_windows_pkg_manager()


def get_linux_pkg_manager() -> Optional[str]:
    manangers = ["apt", "yum"]
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


def get_github_release(name: str, version="latest") -> str:
    owner, repo = name.split("/")
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases/{version}"
    )

    binary_format = binaries[name]
    if binary_format is None:
        binary_format = overrides_by_os[_get_os()].get(name)

    if binary_format is None:
        raise ValueError(f"binary format of `{name}` doesn't exist for `{_get_os()}`")

    if binary_format.startswith("func:"):
        func_to_call = binary_format.replace("func:", "")
        binary_format = globals()[func_to_call]()

    assets = response.json()["assets"]
    for asset in assets:
        if binary_format in asset["name"]:
            return asset["browser_download_url"]

    raise ValueError(
        f"Didn't find binary format of `{name}` in assets:`{[asset['name'] for asset in assets]}`"
    )


def get_nerdfont_name() -> str:
    return "CascadiaCode.tar.xz"


def _get_os() -> str:
    system = platform.system()
    if system == "Linux":
        return "linux"
    elif system == "Darwin":
        return "mac"
    elif system == "Windows":
        return "windows"

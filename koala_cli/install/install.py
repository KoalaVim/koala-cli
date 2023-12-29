#!/usr/bin/env python3

import subprocess
import platform
import requests
import urllib.request
import tempfile
import os

from pathlib import Path
from typing import Any, Callable, Optional, List
from typing_extensions import Annotated

import typer

from .dependencies import pkgs, binaries, overrides_by_os

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
    version = get_bin_attr(name, "version", "latest")
    release = get_github_release(name, version=version)
    installer = get_bin_attr(name, "installer")
    download_and_install(release, installer, dry_run)
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
    if version == "latest":
        version_url = "latest"
    else:
        version_url = f"tags/{version}"

    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases/{version_url}"
    )

    binary_format = get_bin_attr(name, "format")
    if callable(binary_format):
        binary_format = binary_format()

    try:
        assets = response.json()["assets"]
    except KeyError:
        raise ValueError(
            f"Failed to find assets for `{owner}/{repo}` version: {version}"
        )

    for asset in assets:
        if binary_format in asset["name"]:
            return asset["browser_download_url"]

    raise ValueError(
        f"Didn't find binary format of `{name}` in assets:`{[asset['name'] for asset in assets]}`"
    )


def get_bin_attr(name: str, attr: str, default: Optional[Any] = None) -> Any:
    res = binaries[name].get(attr)
    if res is None:
        bin_os = overrides_by_os[_get_os()].get(name)
        if bin_os:
            res = bin_os.get(attr)

    if res is None:
        if default is not None:
            return default
        raise ValueError(f"`{attr}` of `{name}` doesn't exist for `{_get_os()}`")

    return res


def _get_os() -> str:
    system = platform.system()
    if system == "Linux":
        return "linux"
    elif system == "Darwin":
        return "mac"
    elif system == "Windows":
        return "windows"


def download_and_install(url: str, installer: Callable, dry_run: bool) -> Path:
    with tempfile.TemporaryDirectory() as tmpdir_path:
        output_path = Path(tmpdir_path) / Path(os.path.basename(url))
        print(f"Downloading '{url}' to '{output_path}'")
        if not dry_run:
            urllib.request.urlretrieve(url, output_path)
            installer(output_path)

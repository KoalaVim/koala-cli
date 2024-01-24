#!/usr/bin/env python3

import subprocess
import platform
import requests
import urllib.request
import tempfile
import os
import patoolib
import string
import random

from pathlib import Path
from typing import Any, Callable, Optional, List
from typing_extensions import Annotated
from contextlib import ExitStack, contextmanager

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
    keep: Annotated[
        bool,
        typer.Option(help="Keep temporary directories"),
    ] = False,
    skip_download_dir: Annotated[
        Optional[str],
        typer.Option(
            help="Skip the downloads and use the given directory as the downloaded directory"
        ),
    ] = None,
):
    if as_binaries:
        print("Not support yet, sorry :(")
        return typer.Exit(1)

    if skip_download_dir:
        dir = skip_download_dir
    else:
        dir = 'koala_' + ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )

    with temp_dir(dir, False, keep) as base_dir:
        for binary in binaries:
            install_binary(base_dir, binary, dry_run, skip_download_dir)

    pkg_manager = get_os_pkg_manger()
    if pkg_manager is not None:
        install_pkgs(pkgs, pkg_manager, sudo, dry_run)


def install_pkgs(pkg_names: List[str], pkg_manager: str, sudo: bool, dry_run: bool):
    args = []
    if sudo:
        args.append("sudo")

    args += [pkg_manager, "-y", *pkg_names]

    if dry_run:
        print(" ".join(args))
    # subprocess.check_output()


def install_binary(
    base_dir: Path, full_name: str, dry_run: bool, skip_download_dir: Optional[str]
):
    version = get_bin_attr(full_name, "version", "latest")
    release = get_github_release(full_name, version=version)
    installer = get_bin_attr(full_name, "installer")
    download_and_install(
        full_name.split('/')[1],
        base_dir,
        release,
        installer,
        dry_run,
        skip_download_dir,
    )
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

    return None


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

    raise ValueError(f"Invalid os={system}")


def download_and_install(
    name: str,
    base_dir: Path,
    url: str,
    installer: Callable,
    dry_run: bool,
    skip_download: bool,
):
    with temp_dir(str(base_dir / name), True, True) as download_dir:
        output_path = Path(download_dir) / Path(os.path.basename(url))
        if not skip_download:
            print(f"Downloading '{url}' to '{output_path}'")
        if not dry_run:
            if not skip_download:
                urllib.request.urlretrieve(url, output_path)

            out_dir = extract_if_needed(str(output_path))
            installer(out_dir)


@contextmanager
def temp_dir(prefix: str, named: bool, keep: bool) -> Path:
    if named:
        kw_args = {'dir': prefix}
    else:
        kw_args = {'prefix': prefix}

    try:
        if os.path.exists(prefix):
            # Skip creating if already exists
            yield Path(prefix)
            return

        with ExitStack() as stack:
            if keep:
                if named:
                    os.mkdir(prefix)
                    yield Path(prefix)
                else:
                    yield Path(tempfile.mkdtemp(**kw_args))
            else:
                yield Path(stack.enter_context(tempfile.TemporaryDirectory(**kw_args)))
    finally:
        pass


def extract_if_needed(file: str) -> Path:
    out_dir = Path(file + "_extracted")
    if out_dir.exists():
        return out_dir

    patoolib.extract_archive(file, outdir=str(out_dir))
    return out_dir

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

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, List
from typing_extensions import Annotated
from contextlib import ExitStack, contextmanager
from rich.console import Console
from rich.style import Style
from rich.progress import Progress

import typer

from .dependencies import Os, binaries, overrides_by_os
from .installers import Installer

app = typer.Typer(help="Install KoalaVim and dependencies")

# Disable logging from patoolib
import logging.config  # noqa: E402

logging.config.dictConfig({'version': 1, 'disable_existing_loggers': True})


@dataclass
class Config:
    os: Os = None


CFG: Config = None


@app.callback(invoke_without_command=True)
def install(
    dry_run: bool = False,
    os: Annotated[
        Os,
        typer.Option(help="Impersonate OS (only relvant to dry_run)"),
    ] = None,
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
    download: Annotated[
        bool,
        typer.Option(
            help="Skip retrieving url downloads and the download. must be passed with --dry-run"
        ),
    ] = True,
):
    global CFG

    if as_binaries:
        print("Not support yet, sorry :(")
        return typer.Exit(1)

    if os and not dry_run:
        print("You must pass --dry_run with --os")
        return typer.Exit(1)

    if not download and not dry_run:
        print("You must pass --dry_run with --no-download")
        return typer.Exit(1)

    if os == Os.mac:
        # No sudo for mac
        sudo = False
    elif os == Os.windows:
        # Windows always install as binaries for now
        as_binaries = True

    CFG = Config(os=os)

    if skip_download_dir:
        dir = skip_download_dir
    else:
        dir = 'koala_' + ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )

    binaries_to_install = set(binaries.keys())

    if not as_binaries:
        pkg_manager = get_os_pkg_manger()
        if pkg_manager is not None:
            binary_pkgs = {k: v for k, v in binaries.items() if 'pkg' in v}
            binaries_to_install = binaries_to_install - set(binary_pkgs.keys())

            pkgs = [b['pkg'] for b in binary_pkgs.values()]
            install_pkgs(pkgs, pkg_manager, sudo, dry_run)

    with temp_dir(dir, False, keep) as base_dir:
        for binary in binaries_to_install:
            install_binary(base_dir, binary, dry_run, download, skip_download_dir)


def install_pkgs(pkgs: List[str], pkg_manager: str, sudo: bool, dry_run: bool):
    args = []
    if sudo:
        args.append("sudo")

    args += [pkg_manager, "-y", *pkgs]

    if dry_run:
        print(" ".join(args))
    # TODO: uncomment and test
    # subprocess.check_output()


def install_binary(
    base_dir: Path,
    full_name: str,
    dry_run: bool,
    download: bool,
    skip_download_dir: Optional[str],
):
    installer = get_bin_attr(full_name, "installer", False)
    if installer is False:
        c = Console()
        c.rule(style=Style(color='blue3'))
        c.print(
            f"[orange3]Skipping [deep_pink3]{full_name}[/deep_pink3] (no installer)"
        )
        return
    version = get_bin_attr(full_name, "version", "latest")
    if download:
        release = get_github_release(full_name, version=version)
    else:
        release = "NO-DOWNLOAD"

    skip_download = True if skip_download_dir else False
    download_and_install(
        full_name.split('/')[1],
        base_dir,
        release,
        installer,
        dry_run,
        skip_download,
    )
    return


# None = unavailable pkg_manager
def get_os_pkg_manger() -> Optional[str]:
    system = _get_os()
    if system == Os.linux:
        return get_linux_pkg_manager()
    elif system == Os.mac:
        return "brew"
    elif system == Os.windows:
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
            f"Failed to find assets for `{owner}/{repo}` version: {version}, response: {response.json()}"
        )

    for asset in assets:
        if binary_format in asset["name"]:
            return asset["browser_download_url"]

    raise ValueError(
        f"Didn't find binary format of `{name}` in assets:`{[asset['name'] for asset in assets]}`"
    )


def get_bin_attr(name: str, attr: str, default: Optional[Any] = None) -> Any:
    binary = binaries.get(name)
    if binary is None:
        raise ValueError(f"``{name}` doesn't exist for `{_get_os()}`")

    res = binary.get(attr)
    if res is None:
        bin_os = overrides_by_os[_get_os()].get(name)
        if bin_os:
            res = bin_os.get(attr)

    if res is None:
        if default is not None:
            return default
        raise ValueError(f"`{attr}` of `{name}` doesn't exist for `{_get_os()}`")

    return res


def _get_os() -> Os:
    if CFG.os:
        return CFG.os

    system = platform.system()
    if system == "Linux":
        return Os.linux
    elif system == "Darwin":
        return Os.Mac
    elif system == "Windows":
        return Os.windows

    raise ValueError(f"Invalid os={system}")


def download_and_install(
    name: str,
    base_dir: Path,
    url: str,
    installer: Installer,
    dry_run: bool,
    skip_download: bool,
):
    c = Console()
    c.rule(style=Style(color='blue3'))

    with temp_dir(str(base_dir / name), True, True) as download_dir:
        output_path = Path(download_dir) / Path(os.path.basename(url))
        if not skip_download:
            c.print(
                f"[dark_olive_green2]Downloading [deep_pink3]{name}[/deep_pink3] from [cyan]{url}"
            )
        if not dry_run:
            if not skip_download:
                download(url, output_path)
                c.print(
                    f"[dark_olive_green2]Finished! placed at [yellow]{output_path}\n"
                )

            out_dir = extract_if_needed(str(output_path))
            installer(c, out_dir)
            c.print()


def download(url: str, output_path: Path):
    with Progress() as progress:
        task = None

        def _update(i, chunk_size, total_size):
            nonlocal task

            if total_size is not None and task is None:
                task = progress.add_task('', total=total_size)

            if task is not None:
                progress.update(task, advance=i * chunk_size)

        urllib.request.urlretrieve(url, output_path, reporthook=_update)


@contextmanager
def temp_dir(prefix: str, named: bool, keep: bool) -> Iterator[Path]:
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

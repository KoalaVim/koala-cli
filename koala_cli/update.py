#!/usr/bin/env python3

import re
from shutil import copy2
from datetime import datetime
from rich.console import Console
from rich.style import Style
from typing_extensions import Annotated

from koala_cli.lockfile import kvim_lockfile, user_lockfile, _overwrite_lock_file, _lazy_restore
from koala_cli.utils import data_dir, kvim_repo

import typer

app = typer.Typer(help='Update KoalaVim and dependencies')


@app.callback(invoke_without_command=True)
def update(
    target: Annotated[
        str, typer.Option(help="Target commit/branch of KoalaVim for update/downgrade")
    ] = "master",
    remote: Annotated[str, typer.Option(help="Remote target")] = "origin",
    force: Annotated[
        bool, typer.Option(help="Force update (ignore dirty KoalaVim dir)")
    ] = False,
    restore: Annotated[bool, typer.Option(help="Run lazy restore automatically")] = True,
):
    console = Console()

    repo = kvim_repo()
    if repo.is_dirty():
        console.print("Local KoalaVim dir is dirty", style=Style(color="yellow"))
        if not force:
            raise typer.Exit(1)

    repo.remote(remote).fetch()

    # check if target is commit
    m = re.match(r'([a-e0-9]{4,40})', target)
    if m is None:
        target = remote + "/" + target

    console.print(f"Resetting to: {target}")
    repo.head.reset(commit=target, working_tree=True)

    backup_current_lockfile()
    console.print("Overwriting lockfile", style=Style(color="green"))
    _overwrite_lock_file(kvim_lockfile(), user_lockfile(), yes=True)

    if not restore:
        return

    return _lazy_restore()


def backup_current_lockfile():
    console = Console()
    now = datetime.now().strftime('%d-%m-%y_%H:%M:%S')
    file_name = f'lazy-lock-{now}.json.backup'

    src = user_lockfile()
    dst = data_dir() / file_name

    console.print(
        f"Backing up current lockfile to: [yellow]'{dst}'", style=Style(color="green")
    )
    copy2(src, dst)

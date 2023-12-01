#!/usr/bin/env python3

import regex
from shutil import copy2
from datetime import datetime
from rich.console import Console
from rich.style import Style
from typing_extensions import Annotated

from lockfile import kvim_lockfile, user_lockfile, _overwrite_file
from utils import data_dir, kvim_repo

import typer

app = typer.Typer(help='Update KoalaVim and dependencies')

@app.callback(invoke_without_command=True)
def update(
    target: Annotated[str, typer.Option(help="Target commit/branch of KoalaVim for update/downgrade")] = "master",
    remote: Annotated[str, typer.Option(help="Remote target")] = "origin"
):
    console = Console()

    repo = kvim_repo()
    if repo.is_dirty():
        console.print("Local KoalaVim dir is dirty", style=Style(color="yellow"))
        return

    repo.remote(remote).fetch()

    # check if target is commit
    m = regex.match(r'([a-e0-9]{4,40})', target)
    if m is None:
        target = remote + "/" + target

    console.print(f"Resetting to: {target}")
    repo.head.reset(commit=target, working_tree=True)

    backup_current_lockfile()
    console.print("Overwriting lockfile", style=Style(color="green"))
    _overwrite_file(kvim_lockfile(), user_lockfile(), interactive=False)

    console.print("")
    console.print(" >> Run `:Lazy restore` in order to sync plugins to the lock file", style=Style(color="bright_yellow", bold=True))

def backup_current_lockfile():
    console = Console()
    now = datetime.now().strftime('%d-%m-%y_%H:%M:%S')
    file_name = f'lazy-lock-{now}.json.backup'

    src = user_lockfile()
    dst = data_dir() / file_name

    console.print(f"Backing up current lockfile to: [yellow]'{dst}'", style=Style(color="green"))
    copy2(src, dst)

if __name__ == '__main__':
    app()

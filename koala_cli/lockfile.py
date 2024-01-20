import subprocess
from typing import List, NamedTuple

import typer
import json
from typing_extensions import Annotated
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich.style import Style

from koala_cli.utils import kvim_dir, config_dir
from typing import Dict

app = typer.Typer(no_args_is_help=True, help="Manage plugin's lockfile")


@app.command()
def diff(
    filter_missing: Annotated[bool, typer.Option(help='Filter missing plugins')] = False
):
    """
    Show differences of user lock-file from Koala's lock-file
    """
    kvim_lockfile = read_lockfile(kvim_dir())
    user_lockfile = read_lockfile(config_dir())
    lockfile_diff = get_lockfile_diff(user_lockfile, kvim_lockfile, filter_missing)

    table = Table(title="Lock File Diff")
    table.add_column("Name", style="medium_purple3")
    table.add_column("User", style="green")
    table.add_column("KoalaVim", style="cyan")

    for plugin, (user_commit, kvim_commit) in lockfile_diff.items():
        table.add_row(plugin, user_commit, kvim_commit)

    console = Console()
    console.print(table)


Yes = Annotated[bool, typer.Option("--yes", "-y", help="Don't ask for confirmation")]


@app.command()
def overwrite(yes: Yes = False):
    """
    Overwrite user lock-file with Koala's lockfile
    """
    _overwrite_lock_file(kvim_lockfile(), user_lockfile(), yes)
    return _lazy_restore()


@app.command()
def set_koalavim(yes: Yes = False):
    """
    Overwrite Koala's lock-file with user lockfile (used by devs)
    """
    _overwrite_lock_file(user_lockfile(), kvim_lockfile(), yes)


def _overwrite_lock_file(src, dst, yes=False):
    if not yes and not Confirm.ask(f"Confirm overwrite of '{dst}'"):
        return

    with open(src, 'r') as f:
        content: dict = json.load(f)
        content.pop("KoalaVim", None)  # Don't override KoalaVim

        with open(dst, 'w') as out:
            out.write(_format_lazylock(content))

    print(f'{src} -> {dst}')


def _format_lazylock(content: dict) -> str:
    lines = ["{"]
    # json.dumps(content, out, indent=2)
    for plugin, plugin_content in content.items():
        plugin_content = json.dumps(plugin_content)
        plugin_content = plugin_content.replace('{', '{ ')
        plugin_content = plugin_content.replace('}', ' }')

        lines.append(f'  "{plugin}": {plugin_content},')

    # Remove trailing comma after last plugin
    lines[-1] = lines[-1][:-1]

    lines.append("}")

    return '\n'.join(lines)


LOCK_FILE = "lazy-lock.json"


def kvim_lockfile() -> Path:
    return kvim_dir() / LOCK_FILE


def user_lockfile() -> Path:
    return config_dir() / LOCK_FILE


def read_lockfile(path: Path) -> dict:
    with open(path / LOCK_FILE, 'r') as f:
        content = json.load(f)

        plugin_to_commit = {}
        for plugin, info in content.items():
            plugin_to_commit[plugin] = info['commit']

        return plugin_to_commit


Plugin = str


class Diff(NamedTuple):
    old: str
    new: str


MISSING_PLUGIN = "[grey35]N/A"


def get_lockfile_diff(old: dict, new: dict, filter_missing=False) -> Dict[Plugin, Diff]:
    diffs = {}
    for plugin, new_commit in new.items():
        if plugin == "KoalaVim":
            continue  # The user can't never be in the correct commit
        old_commit = old.get(plugin, MISSING_PLUGIN)
        if filter_missing:
            if old_commit == MISSING_PLUGIN:
                continue
        if old_commit != new_commit:
            diffs[plugin] = (old_commit, new_commit)

    return diffs


def _lazy_restore(lockfile_diff: Dict[Plugin, Diff] = {}) -> typer.Exit:
    console = Console()
    console.print("")
    console.print(
        ">> Running `:Lazy restore` (sync plugin versions according to user's lockfile)",
        style=Style(color="bright_yellow", bold=True),
    )

    cmd = ["+LazyRestoreLogged"]
    plugins = list(lockfile_diff.keys())

    if len(plugins) > 0:
        cmd = [" ".join(cmd + plugins)]

        console.print(
            ">> Running restore for the following plugins:\n",
            style=Style(color="bright_yellow", bold=True),
        )
        for plugin, (old_commit, new_commit) in lockfile_diff.items():
            console.print(f"{plugin}: {old_commit[:8]} -> {new_commit[:8]}\n")
    else:
        console.print(
            ">> Updating all plugins..", style=Style(color="bright_yellow", bold=True)
        )

    process = subprocess.Popen(
        ["nvim", "--headless"] + cmd + ["+qa"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    console.print(
        "...",
        style=Style(color="light_salmon3"),
    )
    _, err = process.communicate()

    try:
        res = json.loads(err)

    except json.JSONDecodeError as e:
        console.print(
            "Failed to decode restore output!",
            style=Style(color="bright_red", bold=True),
        )
        console.print(f"Output: {err.decode()}\n")
        console.print(f"Exception: {e}")

        raise typer.Exit(1)

    try:
        if len(res["plugins"]) > 0:
            console.print(
                "`:Lazy restore` finished with errors!\n",
                style=Style(color="bright_red", bold=True),
            )

            for plugin, error in res["plugins"].items():
                console.print(plugin, style=Style(bold=True, underline=True))
                console.print(f"Error: {error}\n")

            raise typer.Exit(1)

        console.print(
            " >> Finished successfully. Restart nvim to take effect",
            style=Style(color="bright_green", bold=True),
        )

    except KeyError as e:
        console.print(
            "Failed to analyze restore result!\n",
            style=Style(color="bright_red", bold=True),
        )
        console.print(f"Key {e} doesn't exist in {res}")

        raise typer.Exit(1)

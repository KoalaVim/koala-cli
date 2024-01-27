from pathlib import Path

from git import Repo


def kvim_dir() -> Path:
    # TODO: [windows]
    return Path.home() / '.local' / 'share' / 'nvim' / 'lazy' / 'KoalaVim'


def config_dir() -> Path:
    # TODO: [windows]
    return Path.home() / '.config' / 'nvim'


def data_dir() -> Path:
    # TODO: [windows]
    return Path.home() / '.local' / 'share' / 'KoalaVim'


# The directory to place `bin`, `lib`, `share` and `man` folders
def base_bin_dir() -> Path:
    # TODO: [windows]
    return Path.home() / '.local'


def kvim_repo() -> Repo:
    return Repo(kvim_dir())

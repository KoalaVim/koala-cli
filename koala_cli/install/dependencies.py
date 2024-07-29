#!/usr/bin/env python3

from typing import Dict, Optional
from enum import Enum

from .installers import (
    get_nerdfont,
    install_fd,
    install_fzf,
    install_neovim,
    install_nerdfont,
    install_ripgrep,
)

Binaries = Dict[str, Dict]
binaries: Binaries = {
    "neovim/neovim": {
        "installer": install_neovim,
        "version": "v0.9.2",
    },
    "ryanoasis/nerd-fonts": {
        "format": get_nerdfont,
        "installer": install_nerdfont,
    },
    "sharkdp/fd": {
        "pkg": "fd",
        "installer": install_fd,
    },
    "BurntSushi/ripgrep": {
        "pkg": "ripgrep",
        "installer": install_ripgrep,
    },
    "junegunn/fzf": {
        "pkg": "fzf",
        "installer": install_fzf,
    },
    "npm": {
        "pkg": "npm",
    },
    # cargo?
    # TODO: treesitter-cli https://github.com/tree-sitter/tree-sitter/blob/master/cli/README.md
}

terminals = {
    "kitty": {
        "desc": "Easy to configure, documented well https://sw.kovidgoyal.net/kitty/conf/",
    },
    "alacritty": {
        "desc": "Fastest terminal, written in rust but has no tab and pane support, recommended for tmux users. Configured via toml",
    },
    "wezterm": {
        "desc": "Works good with windows, configured via lua. https://wezfurlong.org/wezterm/config/files.html",
    },
}


class Os(str, Enum):
    linux = "linux"
    mac = "mac"
    windows = "windows"


overrides_by_os: Dict[Os, Dict] = {
    Os.linux: {
        "apt": {},
        "neovim/neovim": {
            "format": "linux64.tar.gz",
        },
        "sharkdp/fd": {
            "format": "x86_64-unknown-linux-gnu.tar.gz",
        },
        "BurntSushi/ripgrep": {
            "format": "x86_64-unknown-linux-musl.tar.gz",
        },
        "junegunn/fzf": {
            "format": "linux_amd64.tar.gz",
        },
    },
    Os.mac: {
        "brew": {},
        "neovim/neovim": {
            "format": "macos.tar.gz",
        },
    },
    Os.windows: {
        "neovim/neovim": {
            "format": "win64.zip",
        },
        "sharkdp/fd": {
            "format": "x86_64-pc-windows-gnu.zip",
        },
        "BurntSushi/ripgrep": {
            "format": "x86_64-pc-windows-gnu.zip",
        },
        "junegunn/fzf": {
            "format": "windows_amd64.zip",
        },
    },
}

#!/usr/bin/env python3

from .installers import get_nerdfont, install_neovim, install_nerdfont

pkgs = [
    "fd",
    "ripgrep",
    "fzf",
    "npm",
    # cargo?
    # TODO: treesitter-cli https://github.com/tree-sitter/tree-sitter/blob/master/cli/README.md
]

binaries = {
    "neovim/neovim": {
        "installer": install_neovim,
        "version": "v0.9.2",
    },
    "ryanoasis/nerd-fonts": {
        "format": get_nerdfont,
        "installer": install_nerdfont,
    },
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

overrides_by_os = {
    "linux": {
        "apt": {},
        "neovim/neovim": {
            "format": "linux64.tar.gz",
        },
    },
    "mac": {
        "brew": {},
        "neovim/neovim": {
            "format": "macos.tar.gz",
        },
    },
    "windows": {
        "neovim/neovim": {
            "format": "win64.zip",
        },
    },
}

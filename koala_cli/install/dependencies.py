#!/usr/bin/env python3

dependencies = [
    "neovim",
    "fd",
    "nerdfont",
    "ripgrep",
    "fzf",
    "npm",
    # cargo?
    # TODO: treesitter-cli https://github.com/tree-sitter/tree-sitter/blob/master/cli/README.md
]

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
    },
    "mac": {"brew": {}},
}

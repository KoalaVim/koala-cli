#!/usr/bin/env python3

pkgs = [
    "fd",
    "ripgrep",
    "fzf",
    "npm",
    # cargo?
    # TODO: treesitter-cli https://github.com/tree-sitter/tree-sitter/blob/master/cli/README.md
]

binaries = {
    "neovim/neovim": None,
    "ryanoasis/nerd-fonts": "func:get_nerdfont_name",
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
        "neovim/neovim": "linux64.tar.gz",
    },
    "mac": {
        "brew": {},
        "neovim/neovim": "macos.tar.gz",
    },
    "windows": {
        "neovim/neovim": "win64.zip",
    },
}

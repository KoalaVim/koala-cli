#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import List
from rich.prompt import Prompt as RichPrompt
from rich.console import Console
from rich.style import Style

from .dependencies import terminals


@dataclass
class Prompt:
    help: str
    choices: List[str] = None


terminal_help = 'Modern terminal which supports true color\n' + '\n'.join(
    [
        f'\t[prompt.choices]{t}[/prompt.choices] - {v["desc"]}'
        for t, v in terminals.items()
    ]
)


@dataclass
class Options:
    font: str = field(
        default='JetBrainsMono',
        metadata={
            'prompt': Prompt(
                'Nerd Font to download from https://github.com/ryanoasis/nerd-fonts/releases/latest'
            )
        },
    )
    terminal: str = field(
        default='kitty',
        metadata={'prompt': Prompt(terminal_help, choices=terminals.keys())},
    )


def choose_options() -> Options:
    c = Console(style=Style(color='yellow', bold=True))
    c.print('## Install Options ##')
    c.print(
        '* Leave empty to accept default value [prompt.default](example default value)'
    )

    options_params = {}
    for name, f in Options.__dataclass_fields__.items():
        prompt: Prompt = f.metadata['prompt']

        c.rule()
        c.print(prompt.help)
        c.print()
        options_params[name] = RichPrompt.ask(
            'Choose', default=f.default, choices=prompt.choices
        )

    return Options(**options_params)

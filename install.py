#!/usr/bin/env python3

import typer

app = typer.Typer(name="koala-cli", no_args_is_help=True)

@app.command()
def install():
    raise NotImplementedError

if __name__ == '__main__':
    app()

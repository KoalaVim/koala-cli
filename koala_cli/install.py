import typer

app = typer.Typer(help='Install KoalaVim and dependencies')


@app.callback(invoke_without_command=True)
def install():
    print('Sorry, not implemented yet')
    raise typer.Exit(code=1)

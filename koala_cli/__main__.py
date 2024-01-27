import typer

import logging.config

logging.config.dictConfig({'version': 1, 'disable_existing_loggers': True})


from koala_cli import install, update, lockfile, health
from koala_cli.utils import data_dir

app = typer.Typer(
    name='koala', no_args_is_help=True, help='CLI tool to manage KoalaVim'
)
app.add_typer(health.app, name='health')
app.add_typer(install.app, name='install')
app.add_typer(lockfile.app, name='lockfile')
app.add_typer(update.app, name='update')


@app.callback()
def create_data_dir():
    data_dir().mkdir(exist_ok=True)


if __name__ == '__main__':
    app(prog_name='koala-cli')

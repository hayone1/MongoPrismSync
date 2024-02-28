'''This module provides the cli'''

from typing import Optional
import typer
from mongoprism import SUCCESS, __app_name__, __version__, ERRORS
from mongoprism import config as prism_config
from mongoprism import logger

app = typer.Typer()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()
    
@app.command()
def init(
    config_folder_path: Optional[str] = typer.Option(
        "MongoMigrate",
        "--outputfolder",
        "-o",
        help="The folder to place the config file"
    ),
    source_password: Optional[str] = typer.Option(
        "replace_with_password",
        "--source_password",
        "-p"
    ),
    sanitize_config: Optional[bool] = typer.Option(
        False,
        "--sanitize_config",
        "-sc",
        help="""Weather or not the config yaml should be cleaned up.
        This will remove unnecessary fields"""
    ),
    init_template: Optional[bool] = typer.Option(
        True,
        "--init_template",
        "-it",
        help="""Weather or not to initialize the templates.
        This will overwrite templates with the same name."""
    ),
    template_url: Optional[str] = typer.Option(
        "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip",
        "--template_url",
        "-t",
        help="""The url to download the template from. It is only
        effective if config file doesnt exist or sanitize_config is set to true"""
    )
) -> None:
    '''Initialize the application configurations'''
    logger.info("Starting: MongoPrism Init")
    if prism_config.init_app(config_folder_path, source_password, sanitize_config, init_template, template_url) != SUCCESS:
        raise typer.Exit(1)
    
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Shoe the cli version and exit.",
        callback=_version_callback,
        is_eager=True
    )
) -> None:
    return
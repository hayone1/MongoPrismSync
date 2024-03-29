'''This module provides the cli'''

import sys
from typing import Optional
from typing_extensions import Annotated
from kink import inject, di
import typer
from mongocd.Core import config as mongocd_config
from logging import Logger
from mongocd.Interfaces.Services import *
from rich import print
from rich.progress import Progress

app = typer.Typer()
logger = di[Logger]
mongoMigration = di[MongoMigration]
verifyService = di[IVerifyService]
databaseService = di[IDatabaseService]
progress = di[Progress]


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{mongocd_config.__app_name__} v{mongocd_config.__version__}")
        raise typer.Exit()
    
@app.command()
def init(
    config_folder_path: Optional[str] = typer.Option(
        Constants.default_folder,
        "--outputfolder",
        "-o",
        envvar=Constants.config_folder_key,
        help="The folder to place the config file"
    ),
    sanitize_config: Optional[bool] = typer.Option(
        False,
        "--sanitize_config",
        "-s",
        help="""Weather or not the config yaml should be cleaned up.
        This will remove unnecessary fields"""
    ),
    update_templates: Optional[bool] = typer.Option(
        False,
        "--update_templates",
        "-u",
        help="""Weather or not to download the templates.
        This will overwrite existing templates with the same name."""
    ),
    template_url: Optional[str] = typer.Option(
        "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip",
        "--template_url",
        "-t",
        help="""The url to download the template from. It is only
        effective if config file doesnt yet exist or sanitize_config is set to true"""
    )
) -> None:
    '''Initialize the application configurations and verify that the source database is reacheable'''
    print(f"Starting: {mongocd_config.__app_name__} {init.__name__}")

    if config_folder_path == Constants.default_folder:
        logger.info(f"Using default working folder: {Constants.default_folder}")

    if config_folder_path is None:
        config_folder_path = typer.prompt("Enter path of working directory(absolute/relative): ")
    with progress:
        init_config_result = mongocd_config.init_configs(config_folder_path, sanitize_config,
                                                     update_templates, template_url)
    if init_config_result != ReturnCode.SUCCESS:
        raise typer.Exit(init_config_result.value)
    print(f"{Constants.rich_completed} {mongocd_config.__app_name__} {init.__name__}")

@app.command()
def build(
    config_folder_path = Annotated[str, typer.Option(
        Constants.default_folder,
        "--outputfolder",
        "-o",
        envvar=Constants.config_folder_key,
        help="The folder to place the config file"
    )],
    source_password = Annotated[str, typer.Option(
        None,
        "--source_password",
        "-p",
        envvar=Constants.mongo_source_pass,
        help="Password of the source database"
    )],
    environment = Annotated[str, typer.Option(
        Constants.default_environment,
        "--environment",
        "-e",
        help="Password of the source database"
    )],
):
    '''Pull data from source database and apply transformations based on given configuration'''
    print(f"Starting: {mongocd_config.__app_name__} {weave.__name__}")
    reload_dependencies = False
    # ensure environment vriables are set and refresh dependencies afterwards if required
    if os.getenv(Constants.config_folder_key) is None:
        reload_dependencies = True
        #set both config_folder_path and the env variable
        os.environ[Constants.config_folder_key] = config_folder_path = \
            (config_folder_path 
             or typer.prompt("Working dirctory not set. Enter path of working directory(absolute/relative)"))
        
    if os.getenv(Constants.mongo_source_pass) is None:
        reload_dependencies = True
        #set both source_password and the env variable
        source_password = os.environ[Constants.mongo_source_pass] = \
            (source_password 
             or typer.prompt("Source password not set. Enter password of source mongodb", hide_input=True))

    #refresh dependencies
    if reload_dependencies == True:
        # utils.reload_program(mongocd_config.__app_name__, app)
        inject_result = mongocd_config.inject_dependencies()
        # these feel redundant, but I cant seem to simulate a get accessor correctly in python
        if inject_result != ReturnCode.SUCCESS:
            typer.Exit(inject_result)
        global mongoMigration; mongoMigration = di[MongoMigration]
        global verifyService; verifyService = di[IVerifyService]
        global databaseService; databaseService = di[IDatabaseService]

    if verifyService is None:
        logger.fatal(f"verifyService dependency uninitialized")
        raise typer.Exit(ReturnCode.UNINITIALIZED.value)
    
    with progress:
        # progress.add_task("test_task")
        verify_connectivity = verifyService.verify_connectivity(source_password)
        if verify_connectivity != ReturnCode.SUCCESS:
            raise typer.Exit(ReturnCode.DB_ACCESS_ERROR.value)
        
        verify_database = verifyService.verify_databases()
        if verify_database != ReturnCode.SUCCESS:
            raise typer.Exit(ReturnCode.DB_ACCESS_ERROR.value)
        # print("[green] Connection to database established Successfully!")
    
        asyncio.run(databaseService.generate_syncscripts_async())

    print(f"{Constants.rich_completed} {mongocd_config.__app_name__} {weave.__name__}")
    #VerifyDatabases
    
    
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the cli version and exit.",
        callback=_version_callback,
        is_eager=True
    )
) -> None:
    return
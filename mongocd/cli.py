'''This module provides the cli'''

import sys
from typing import Optional
from typing_extensions import Annotated
from kink import inject, di
import typer
from mongocd.Core import config as mongocd_config
from logging import Logger
from rich import print
from rich.progress import Progress
from mongocd.Domain.MongoMigration import MongoMigration
from mongocd.Interfaces.Services import *

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
    config_folder_path: Annotated[Optional[str], typer.Option(
        "--outputfolder",
        "-o",
        envvar=Constants.CONFIGFOLDER.value,
        help="The folder to place the config file"
    )] = Constants.CONFIGFOLDER.value,
    sanitize_config: Annotated[Optional[bool], typer.Option(
        "--sanitize-config",
        "-s",
        help=("Weather or not the config yaml should be cleaned up."
        "This will remove unnecessary fields")
    )] = False,
    update_templates: Annotated[Optional[bool], typer.Option(
        "--update-templates",
        "-u",
        help="""Weather or not to download the templates.
        This will overwrite existing templates with the same name."""
    )] = False,
    template_url: Optional[str] = typer.Option(
        "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip",
        "--template-url",
        "-t",
        help="""The url to download the template from. It is only
        effective if config file doesnt yet exist or sanitize_config is set to true"""
    )
) -> None:
    '''Initialize the application configurations and verify that the source database is reacheable'''
    print(f"Starting: {mongocd_config.__app_name__} {init.__name__}")

    if config_folder_path == Constants.CONFIGFOLDER.value:
        logger.info(f"Using default working folder: {Constants.CONFIGFOLDER.value}")

    if config_folder_path is None:
        config_folder_path = typer.prompt("Enter path of working directory(absolute/relative): ")
    with progress:
        init_config_result = mongocd_config.init_configs(config_folder_path, sanitize_config,
                                                     update_templates, template_url)
    if init_config_result != ReturnCode.SUCCESS:
        raise typer.Exit(init_config_result.value)
    print(f"{Constants.rich_completed.value} {mongocd_config.__app_name__} {init.__name__}")

# @app.command()
# def build(
#     source_password: Annotated[str, typer.Option(
#         "--source_password",
#         "-p",
#         envvar=Constants.MONGOSOURCEPASSWORD.name,
#         help="Password of the source database",
#         prompt=True,
#         hide_input=True
#     )],
#     config_folder_path: Annotated[str, typer.Option(
#         "--outputfolder",
#         "-o",
#         envvar=Constants.CONFIGFOLDER.name,
#         help="The folder to place the config file",
#         prompt=True
#     )] = Constants.CONFIGFOLDER.value,
#     render_env:  Annotated[list[str], typer.Option(
#         "--render-env",
#         "-r",
#         envvar=Constants.RENDER_ENV.name,
#         help=("The environments to be considered for this build."
#         "Existing environment renders will be untouched if not included here."),
#         prompt=True
#     )] = Constants.RENDER_ENV.value
# ):
#     '''Pull data from source database and apply transformations based on given configuration'''
#     print(f"Starting: {mongocd_config.__app_name__} {build.__name__}")
#     reload_dependencies = False
#     # ensure environment variables are set and refresh dependencies afterwards if required
#     if os.getenv(Constants.CONFIGFOLDER.name) is None:
#         reload_dependencies = True
#         #set both config_folder_path and the env variable
#         os.environ[Constants.CONFIGFOLDER.name] = config_folder_path
        
#     if os.getenv(Constants.MONGOSOURCEPASSWORD.name) is None:
#         reload_dependencies = True
#         #set both source_password and the env variable
#         os.environ[Constants.MONGOSOURCEPASSWORD.name] = source_password
#     # neec to check for string in case it is gotten from env variables
#     if isinstance(render_env, str):
#         try:
#             render_env = json.load(render_env)
#         except Exception as ex:
#             logger.fatal((f"Unable to convert render_env: {render_env} to valid list"
#                 f"ensure it is a correctly formatter json list | {ex}"))
#             raise typer.Exit(ReturnCode.INVALID_CONFIG_ERROR.value)
#     #refresh dependencies
#     if reload_dependencies == True:
#         # utils.reload_program(mongocd_config.__app_name__, app)
#         inject_result = mongocd_config.inject_dependencies()
#         # these feel redundant, but I cant seem to simulate 
#         # a get accessor correctly in python to always fetch the latest dependencies
#         if inject_result != ReturnCode.SUCCESS: typer.Exit(inject_result)

#     if di[IVerifyService] is None:
#         logger.fatal(f"verifyService dependency uninitialized")
#         raise typer.Exit(ReturnCode.UNINITIALIZED.value)
    
#     with progress:
#         # progress.add_task("test_task")
#         verify_connectivity = di[IVerifyService].verify_connectivity(source_password)
#         if verify_connectivity != ReturnCode.SUCCESS:
#             raise typer.Exit(ReturnCode.DB_ACCESS_ERROR.value)
        
#         verify_database = di[IVerifyService].verify_databases()
#         if verify_database != ReturnCode.SUCCESS:
#             raise typer.Exit(ReturnCode.DB_ACCESS_ERROR.value)
#         # print("[green] Connection to database established Successfully!")
    
#         asyncio.run(di[IDatabaseService].generate_syncscripts_async())

#     print(f"{Constants.rich_completed} {mongocd_config.__app_name__} {build.__name__}")
    
    
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
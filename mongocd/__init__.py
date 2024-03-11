'''Top-Level packages'''

from mongocd.Core.config import *
inject_result = inject_dependencies()
if inject_result != ReturnCodes.SUCCESS:
    typer.Exit(inject_result)

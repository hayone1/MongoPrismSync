"""Top-Level packages"""

import typer
from mongocd.Core.config import ReturnCode, inject_dependencies
inject_result = inject_dependencies()
if inject_result != ReturnCode.SUCCESS:
    typer.Exit(inject_result)

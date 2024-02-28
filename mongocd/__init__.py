'''Top-Level packages'''

__app_name__ = "mongoprism"
__version__ = '0.0.1'

import logging
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler



(
    SUCCESS,
    ARG_ERROR,
    DIR_ACCESS_ERROR,
    READ_CONFIG_ERROR,
    INVALID_CONFIG_ERROR,
    EXTRACT_FILE_ERROR,
) = range(6)

ERRORS = {
    ARG_ERROR: "Argument parse error",
    DIR_ACCESS_ERROR: "Directory access error",
    READ_CONFIG_ERROR: "config access error",
    INVALID_CONFIG_ERROR: "invalid configuration error"
}

#################logging##################
handler = logging.StreamHandler()  # Or FileHandler or anything else
# Configure the fields to include in the JSON output. message is the main log string itself
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)

# Normally we would attach the handler to the root logger, and this would be unnecessary
# logger.propagate = False
#################logging##################
'''Top-Level packages'''

__app_name__ = "mongoprism"
__version__ = '0.0.1'

import logging
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler





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
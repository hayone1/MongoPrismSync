'''Top-Level packages'''

__app_name__ = "mongoprism"
__version__ = '0.0.1'

(
    SUCCESS,
    ARG_ERROR,
    DIR_ACCESS_ERROR,
    READ_CONFIG_ERROR,
    INVALID_CONFIG_ERROR
) = range(5)

ERRORS = {
    ARG_ERROR: "Argument parse error",
    DIR_ACCESS_ERROR: "Directory access error",
    READ_CONFIG_ERROR: "config access error",
    INVALID_CONFIG_ERROR: "invalid configuration error"
}
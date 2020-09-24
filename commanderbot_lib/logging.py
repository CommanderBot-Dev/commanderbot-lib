import logging.config
from logging import Logger

# Use colorlog as an optional dependency - which in turn uses colorama - for prettier logs.
# NOTE Colours may not work on Git Bash. See: https://github.com/tartley/colorama/pull/226
try:
    import colorlog
except:
    pass


LOG_LEVELS = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)

LOG_FORMAT_BASIC = "%(log_color)s%(message)s"
LOG_FORMAT_DETAILED = "%(log_color)s%(asctime)s %(levelname)-8s [%(name)s] %(message)s"

LOG_COLORS = {
    LOG_LEVELS[0]: "cyan",
    LOG_LEVELS[1]: "green",
    LOG_LEVELS[2]: "yellow",
    LOG_LEVELS[3]: "red",
    LOG_LEVELS[4]: "red,bg_white",
}


def setup_logging(
    level: str = logging.WARNING,
    detailed: bool = False,
    log_format: str = None,
    log_colors: dict = LOG_COLORS,
):
    log_format = log_format or (LOG_FORMAT_DETAILED if detailed else LOG_FORMAT_BASIC)
    log_handler = logging.StreamHandler()

    try:
        log_handler.setFormatter(colorlog.ColoredFormatter(fmt=log_format, log_colors=log_colors))
    except:
        print(
            "Terminal colors (via colorama and/or colorlog) are unavailable; using basic logging instead."
        )

    logging.basicConfig(level=level, handlers=[log_handler])


def get_logger(name: str = __name__) -> Logger:
    return logging.getLogger(name)


def get_clogger(cog, guild=None) -> Logger:
    if guild:
        return logging.getLogger(f"{cog.qualified_name}@{guild}")
    return logging.getLogger(f"{cog.qualified_name}")


def preview_logging():
    log = get_logger()
    log.debug("debug")
    log.info("info")
    log.warning("warning")
    log.error("error")
    log.critical("critical")
    try:
        raise ValueError("don't worry this is a fake error")
    except:
        log.exception("exception")

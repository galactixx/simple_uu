import logging

from rich.logging import RichHandler

def set_up_logger(name: str) -> logging.Logger:
    """
    The setup for the package logger. Logger only has streaming capabilities.

    Args:
        name (str): The name of the module in which the logger resides.

    Returns:
        Logger: A Logger instance.
    """
    root_logger = logging.getLogger('simple_uu')

    if name != root_logger.name:
        logger = root_logger.getChild(name)
    else:
        logger = root_logger

    # Set handler for logger if none exist
    if not logger.handlers:
        logger.handlers.clear()

        handler = RichHandler(rich_tracebacks=True, markup=False)
        formatter = logging.Formatter("%(name)s - %(message)s")
        handler.setFormatter(formatter)

        logger.setLevel(level=logging.DEBUG)

        logger.addHandler(handler)
        logger.propagate = False

    return logger
import logging


def configure_logging():
    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("azure."):
            logging.getLogger(logger_name).setLevel(logging.WARNING)

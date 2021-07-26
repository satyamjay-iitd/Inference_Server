import logging


def get_logger(logfile_path, name, level, log_format):
    handler = logging.FileHandler(logfile_path)
    handler.setFormatter(log_format)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

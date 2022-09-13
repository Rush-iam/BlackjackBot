import logging


logger = logging.getLogger('app')


def setup_logging() -> None:
    basic_format = '[%(asctime)s] %(levelname)-8s'
    timestamp_format = '%y-%m-%d %H:%M:%S'

    logging.basicConfig(
        level=logging.INFO,
        format=f'{basic_format} %(message)s',
        datefmt=timestamp_format,
    )
    logging.logThreads = False
    logging.logProcesses = False
    logging.logMultiprocessing = False

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(
        logging.Formatter(
            fmt=f'{basic_format} [%(module)s:%(funcName)s]: %(message)s',
            datefmt=timestamp_format,
        )
    )

    logger.addHandler(stderr_handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)

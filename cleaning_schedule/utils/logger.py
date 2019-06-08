import logging
import sys


def configure_logging(name, level=logging.INFO):
    log = logging.getLogger(name)
    log.setLevel(level)
    log.addHandler(create_stream_handler())
    return log


def create_stream_handler(log_format='%(asctime)s %(name)s %(levelname)s %(message)s'):
    stream = sys.stdout
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(log_format))
    return stream_handler

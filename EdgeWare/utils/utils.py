import logging
import os
import platform
import time

from utils.paths import LOG_PATH


def init_logging(filename, source=None):
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    log_time = time.asctime().replace(" ", "_").replace(":", "-")
    log_file = f"{log_time}-{filename}.txt"
    logging.basicConfig(filename=LOG_PATH / log_file, format="%(levelname)s:%(message)s", level=logging.DEBUG, force=True)
    if source:
        logging.info(f"Started {source} logging successfully.")

    return log_file


def is_linux():
    return platform.system() == "Linux"


def is_windows():
    return platform.system() == "Windows"


def is_mac():
    return platform.system() == "Darwin"


if is_linux():
    from .linux import *
elif is_windows():
    from .windows import *
elif is_mac():
    from .mac import *
else:
    raise RuntimeError("Unsupported operating system: {}".format(platform.system()))

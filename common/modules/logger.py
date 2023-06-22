import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("log.log")
formatter = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(threadName)s - %(funcName)s - %(message)s",
    datefmt="%H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

logging.disable(logging.CRITICAL)

import logging


class MyLogger(logging.Logger):
    def __init__(self, name: str, filename="log.log") -> None:
        super().__init__(name)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler(filename)
        self.formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(threadName)s - %(funcName)s - %(message)s",
            datefmt="%H:%M:%S"
        )
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

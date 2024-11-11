import structlog
import logging


def get_logger(cls: str):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(filename="app.log"),
        ],
    )
    return structlog.get_logger().bind(cls=cls)

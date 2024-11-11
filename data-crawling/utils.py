import structlog
from errors import ImproperlyConfigured
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


def user_to_names(user: str | None) -> tuple[str, str]:
    if user is None:
        raise ImproperlyConfigured("no username provided")

    name_token = user.split(" ")
    if len(name_token) == 0:
        return ImproperlyConfigured("no username provided")
    elif len(name_token) == 1:
        first_name, last_name = name_token[0], ""
    else:
        first_name, last_name = "".join(name_token[:-1]), name_token[-1]
    return first_name, last_name

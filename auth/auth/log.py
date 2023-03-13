from logging.config import dictConfig


# TODO copy openstack logger configuration
def configure_logging():
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                }
            },
            "loggers": {
                "root": {"level": "INFO", "handlers": ["default"]},
                "auth.util": {"level": "INFO"},
            },
        }
    )

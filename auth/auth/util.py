import logging
import logging.config

log = logging.getLogger("auth.util")


# TODO: copy openstack logger configuration
def setup_logging():
    logging.config.dictConfig(
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

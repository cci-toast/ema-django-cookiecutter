from functools import partial

import envparse

from jslog4kube import LOGGING

from .formatters import get_formatter


def config_loggers(proj_name: str, proj_dir: str, env: envparse.Env):
    LOGGING["formatters"]["json"] = {"()": partial(get_formatter, proj_name, proj_dir)}

    # Handle local logging of 'user' logger to local ElasticSearch
    # using docker-compose.  This should not be on in deployed environments
    LOCAL_LOGGING = env("LOCAL_LOGGING", cast=bool, default=False)
    EMONEY_LOGGER_NAME = "emoney"
    ES_HOST = env("ES_HOST", default="elasticsearch")
    ES_PORT = env("ES_PORT", cast=int, default=9200)

    LOGGING["filters"]["require_debug_false"] = {
        "()": "django.utils.log.RequireDebugFalse"
    }
    LOGGING["loggers"][""] = {
        "handlers": ["json-stdout"],
        "formatters": ["json"],
        "propagate": True,
        "filters": ["default"],
        "level": "INFO",
    }

    if LOCAL_LOGGING:
        from .cmres import PatchedHandler

        LOGGING["handlers"]["es"] = {
            "level": "DEBUG",
            "class": "structlogging.cmres.PatchedHandler",
            "hosts": [{"host": ES_HOST, "port": ES_PORT}],
            "es_index_name": EMONEY_LOGGER_NAME,
            "auth_type": PatchedHandler.AuthType.NO_AUTH,
            "use_ssl": False,
            "formatter": "json",
        }
        LOGGING["loggers"][""]["handlers"].append("es")
        LOGGING["loggers"]["elasticsearch"] = {
            "handlers": ["json-stdout"],
            "level": "WARN",
        }
    else:
        # TBD This will fail, replace with some other production level logging
        rollbar_environment = env("ROLLBAR_ENVIRONMENT", default="local")
        LOGGING["handlers"]["rollbar"] = {
            "filters": ["require_debug_false"],
            "access_token": env("ROLLBAR_ACCESS_TOKEN"),
            "environment": rollbar_environment,
            "class": "rollbar.logger.RollbarHandler",
            "enabled": rollbar_environment != "local",
            "level": "WARNING",
        }
        LOGGING["loggers"][""]["handlers"].append("rollbar")

    return LOGGING

from logging.config import dictConfig

import envparse

from .loggers import config_loggers
from .structlogging import structlog_configure


def django_configure(project_name: str, project_dir: str, env: envparse.Env):
    structlog_configure(project_name, project_dir)
    config = config_loggers(project_name, project_dir, env)
    dictConfig(config)
    return config


def celery_configure(project_name: str, project_dir: str, env: envparse.Env):
    from celery.signals import after_setup_task_logger

    config = config_loggers(project_name, project_dir, env)
    config["loggers"][""] = {"handlers": ["json-stdout"]}

    @after_setup_task_logger.connect(weak=False)
    def setup_task_loggers(sender, logger, *args, **kwargs):
        dictConfig(config)

    return config

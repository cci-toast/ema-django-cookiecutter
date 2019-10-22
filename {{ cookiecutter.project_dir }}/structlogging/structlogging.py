import structlog

from .processors import get_shared_processors


def structlog_configure(proj_name: str, proj_dir: str):
    structlog.configure(
        processors=get_shared_processors(proj_name, proj_dir)
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

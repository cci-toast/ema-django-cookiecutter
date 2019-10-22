import structlog

from .processors import get_shared_processors


def get_formatter(proj_name: str, proj_dir: str) -> structlog.stdlib.ProcessorFormatter:
    return structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=get_shared_processors(proj_name, proj_dir),
    )

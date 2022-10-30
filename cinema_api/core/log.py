from __future__ import annotations

import logging
from types import FrameType
from typing import Callable, cast

import loguru
from loguru import logger

main_logger: loguru.Logger


def filter_by_name(name: str) -> Callable:
    """Filter function for write message with 'name' in extra

    Args:
        name (str): Name of binded logger

    Returns:
        Callable: function for filtering message
    """
    return lambda record: record["extra"].get("name") == name


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )

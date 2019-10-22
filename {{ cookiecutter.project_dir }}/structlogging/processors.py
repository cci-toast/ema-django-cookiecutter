# -*- coding: utf-8 -*-

import inspect
import os
import sys

from types import FrameType
from typing import Any, Callable, Dict, Tuple

from django.views.debug import CLEANSED_SUBSTITUTE, cleanse_setting

import structlog

StrDict = Dict[str, Any]


class ServiceName:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, logger, method_name: str, event_dict: StrDict):
        """
        Adds the service name to the event dict.
        """
        event_dict["service"] = self.name
        return event_dict


def add_request(logger, method_name: str, event_dict: StrDict):
    """
    Extracts the request id and remove the `request` object from locals (it doesn't
    print out useful info anyway).
    """
    request = None
    if "request" in event_dict.get("locals", {}):
        request = event_dict["locals"].pop("request")
    elif "request" in event_dict.get("extra", {}):
        request = event_dict["extra"].pop("request")
    if request is not None:
        if hasattr(request, "META"):
            event_dict["remote_addr"] = request.META["REMOTE_ADDR"]
        elif hasattr(request, "getpeername"):
            try:
                event_dict["remote_addr"] = request.getpeername()[0]
            except OSError:
                event_dict["remote_addr"] = "N/A"
        if hasattr(request, "method"):
            event_dict["method"] = request.method
        if hasattr(request, "build_absolute_uri"):
            event_dict["url"] = request.build_absolute_uri()
        if hasattr(request, "id"):
            event_dict["request_id"] = request.id
    return event_dict


def add_task_info(logger, method_name: str, event_dict: StrDict):
    """
    Adds the task info from celery into the event dict.
    """
    try:
        from celery._state import get_current_task

        task = get_current_task()
    except ImportError:
        pass
    else:
        if task is not None:
            event_dict["task_id"] = task.request.id
            event_dict["celery_task_name"] = task.name
            event_dict["hostname"] = task.request.hostname
    return event_dict


def add_extra(logger, method_name: str, event_dict: StrDict):
    defaults = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "asctime",
    }
    if "_record" in event_dict:
        record_dict = event_dict["_record"].__dict__
        extra_keys = record_dict.keys() - defaults
        if extra_keys:
            event_dict["extra"] = {k: record_dict[k] for k in extra_keys}
    return event_dict


class LocalVariables:
    always_sensitive: Tuple[str, ...] = (
        "first_name",
        "last_name",
        "email",
        "sender",
        "recipient",
    )

    def __init__(self, proj_dir: str, replacement: str = CLEANSED_SUBSTITUTE):
        self.proj_dir = proj_dir
        self.replacement = replacement

    def _replace_sensitive(
        self, key: str, value: Any, sensitive_variables: Tuple[str, ...]
    ) -> Any:
        """
        Replaces a single key-value pair with a redacted value, if the the key is
        in `sensitive_variables`.
        """
        cleansed = value
        if value == CLEANSED_SUBSTITUTE:
            return self.replacement
        if isinstance(cleansed, dict):
            cleansed = {
                k: self._replace_sensitive(k, v, sensitive_variables)
                for k, v in value.items()
            }
        else:
            if sensitive_variables == "__ALL__" or key in sensitive_variables:
                return self.replacement
        return cleansed

    def _cleanse_variables(
        self, variables: StrDict, sensitive_variables: Tuple[str, ...]
    ) -> StrDict:

        cleansed = {}
        for k, v in variables.items():
            if k.startswith("__") and k.endswith("__"):
                continue

            cleansed_value = cleanse_setting(k, v)
            cleansed[k] = self._replace_sensitive(
                k, cleansed_value, self.always_sensitive + sensitive_variables
            )
        return cleansed

    @staticmethod
    def _get_sensitive_variables(frame: FrameType) -> Tuple[str, ...]:
        if frame is None:
            return tuple()

        wrapper = frame.f_locals.get("sensitive_variables_wrapper")
        if wrapper is not None:
            return getattr(wrapper, "sensitive_variables", [])
        return tuple()

    @staticmethod
    def _is_sensitive_frame(frame: FrameType) -> bool:
        """
        Checks if the frame has some sensitive variables declared.
        """
        return (
            frame.f_code.co_name == "sensitive_variables_wrapper"
            and "sensitive_variables_wrapper" in frame.f_locals
        )

    def _is_frame_from_project(self, frame: FrameType) -> bool:
        """
        Check if the frame is from a file belonging to the project, ie: not from
        any installed library.

        The way we differentiate is a little naive: We just check if the file is
        inside the project's directory, but exclude _this one_ particular file you're
        reading.
        """

        return frame.f_globals.get("__file__", "") != os.path.abspath(
            __file__
        ) and frame.f_globals.get("__file__", "").startswith(self.proj_dir)

    def _find_exception_frame(
        self, excinfo, check_fn: Callable[[FrameType], bool]
    ) -> FrameType:
        """
        Walk the traceback down until it find a frame that passes the ``check_fn`` test
        function and returns it.
        """
        tb = sys.exc_info()[2] or excinfo[2]
        current_frame = tb.tb_frame
        while tb is not None:
            # Support for __traceback_hide__ which is used by a few libraries
            # to hide internal frames.
            if tb.tb_frame.f_locals.get("__traceback_hide__"):
                tb = tb.tb_next
                continue

            current_frame = tb.tb_frame
            if check_fn(current_frame):
                break
            tb = tb.tb_next
        return current_frame

    def _is_exc_frame(self, frame: FrameType) -> bool:
        # For exceptions, we just go all the way down.
        return False

    def _find_frame(self, check_fn: Callable[[FrameType], bool]) -> FrameType:
        """
        Walk the stack back up until it find a frame that passes the ``check_fn`` test
        function and returns it.
        """
        tb_frame = inspect.stack()[0].frame
        current_frame = tb_frame.f_back
        while current_frame is not None:
            if check_fn(current_frame):
                break
            current_frame = current_frame.f_back
        return current_frame

    def __call__(self, logger, method_name: str, event_dict: StrDict) -> StrDict:
        if event_dict.get("exc_info"):
            frame = self._find_exception_frame(
                event_dict["exc_info"], self._is_exc_frame
            )
            sensitive_variables_frame = self._find_exception_frame(
                event_dict["exc_info"], self._is_sensitive_frame
            )
        else:
            frame = self._find_frame(self._is_frame_from_project)
            sensitive_variables_frame = self._find_frame(self._is_sensitive_frame)

        if frame is not None:
            local_variables = frame.f_locals
            sensitive_variables = self._get_sensitive_variables(
                sensitive_variables_frame
            )
            if local_variables is not None:
                event_dict["locals"] = self._cleanse_variables(
                    local_variables, sensitive_variables
                )
        return event_dict


def copy_to_record(logger, name, event_dict):
    if "_record" in event_dict:
        for k, v in event_dict.items():
            setattr(event_dict["_record"], k, v)
    return event_dict


def get_shared_processors(proj_name: str, proj_dir: str):
    return [
        add_extra,
        ServiceName(proj_name),
        add_task_info,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        LocalVariables(proj_dir),
        add_request,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        copy_to_record,
        structlog.processors.UnicodeDecoder(),
    ]

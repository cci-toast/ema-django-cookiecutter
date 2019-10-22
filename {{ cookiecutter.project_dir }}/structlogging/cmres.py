import json
import logging

from cmreslogging.handlers import CMRESHandler


class PatchedHandler(CMRESHandler):
    def __init__(self, *args, **kwargs):
        self.formatted = False
        super().__init__(*args, **kwargs)

    def format(self, record):
        if not self.formatted:
            return super().format(record)
        return record

    def emit(self, record):
        """ Emit overrides the abstract logging.Handler logRecord emit method

        Format and records the log

        :param record: A class of type ```logging.LogRecord```
        :return: None
        """
        self.formatted = False
        formatted_record = self.format(record)
        deserialized = json.loads(formatted_record)
        self.formatted = True
        record = logging.makeLogRecord(deserialized)
        record.msg = deserialized["event"]
        super().emit(record)
        self.formatted = False

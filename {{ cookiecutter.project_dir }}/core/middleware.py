import structlog

from django.conf import settings


class StructLog(object):
    """
    Setup structlog object
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger_name = getattr(settings, 'EMONEY_LOGGER_NAME', 'emoney')
        logger = structlog.get_logger(logger_name)

        logger = logger.bind(
            request_id=request.id,
        )
        request.logger = logger

        response = self.get_response(request)

        return response

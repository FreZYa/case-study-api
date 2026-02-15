import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Logs incoming requests with method, path, status code and duration."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start_time) * 1000

        logger.info(
            "%s %s %s %.0fms",
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
        )
        return response

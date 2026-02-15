import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class ApplicationError(APIException):
    """Base exception for application-specific errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An application error occurred."
    default_code = "APPLICATION_ERROR"

    def __init__(self, message: str = None, error_code: str = None, details: dict = None):
        self.message = message or self.default_detail
        self.error_code = error_code or self.default_code
        self.details = details
        super().__init__(detail=self.message)


class NotFoundError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "NOT_FOUND"


class ValidationError(ApplicationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation error."
    default_code = "VALIDATION_ERROR"


class AuthenticationError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication failed."
    default_code = "AUTHENTICATION_ERROR"


class DuplicateError(ApplicationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Resource already exists."
    default_code = "DUPLICATE_ERROR"


def custom_exception_handler(exc, context):
    """Centralized exception handler that returns standardized error responses."""
    response = exception_handler(exc, context)

    if isinstance(exc, ApplicationError):
        error_data = {
            "success": False,
            "error": exc.error_code,
            "message": exc.message,
        }
        if exc.details:
            error_data["details"] = exc.details
        return Response(error_data, status=exc.status_code)

    if response is not None:
        error_code = _get_error_code(response.status_code)
        message = _extract_message(response.data)
        error_data = {
            "success": False,
            "error": error_code,
            "message": message,
        }
        if isinstance(response.data, dict):
            details = {k: v for k, v in response.data.items() if k != "detail"}
            if details:
                error_data["details"] = details
        response.data = error_data
        return response

    logger.exception("Unhandled exception: %s", exc)
    return Response(
        {
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _get_error_code(status_code: int) -> str:
    codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        500: "INTERNAL_SERVER_ERROR",
    }
    return codes.get(status_code, "ERROR")


def _extract_message(data) -> str:
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        messages = []
        for key, value in data.items():
            if isinstance(value, list):
                messages.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                messages.append(f"{key}: {value}")
        return "; ".join(messages) if messages else "An error occurred."
    if isinstance(data, list):
        return "; ".join(str(item) for item in data)
    return str(data)

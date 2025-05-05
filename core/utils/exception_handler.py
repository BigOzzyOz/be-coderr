from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    MethodNotAllowed,
)
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response

    if isinstance(exc, (NotFound, Http404, ObjectDoesNotExist)):
        logger.info(f"Resource not found: {exc.__class__.__name__} - {str(exc)}")
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, PermissionDenied):
        logger.warning(f"Permission denied: {str(exc)}")
        return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

    if isinstance(exc, ValidationError):
        logger.warning(f"Validation error: {exc.detail}")
        return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        logger.warning(f"Authentication error: {str(exc)}")
        return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, MethodNotAllowed):
        logger.warning(f"Method not allowed: {str(exc)}")
        return Response({"detail": str(exc)}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    logger.error(f"Unhandled exception caught: {exc.__class__.__name__} - {str(exc)}", exc_info=True)

    if settings.DEBUG:
        error_detail = f"Internal server error: {exc.__class__.__name__} - {str(exc)}"
    else:
        error_detail = "Internal server error."

    return Response({"detail": error_detail}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

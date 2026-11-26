from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler

from budgets.errors import CategoryInUseError


class Conflict(APIException):
    status_code = 409
    default_detail = "The request conflicts with the current state of the resource."
    default_code = "conflict"


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            detail = exc.message_dict
            if "__all__" in detail:
                detail[api_settings.NON_FIELD_ERRORS_KEY] = detail.pop("__all__")
        else:
            detail = {"detail": exc.messages}
        exc = DRFValidationError(detail=detail)
    elif isinstance(exc, CategoryInUseError):
        exc = Conflict(detail=str(exc))

    return exception_handler(exc, context)

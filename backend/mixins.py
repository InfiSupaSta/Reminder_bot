from typing import Union, Tuple, Any


class MakeExceptionMixin:

    @staticmethod
    def _make_exception_message(exception: Exception) -> Union[str, Tuple[Any]]:
        try:
            error_message: str = exception.args[0]
            error_detail = error_message.split('DETAIL')[1].strip('\n')
            return error_detail
        except Exception:
            return exception.args

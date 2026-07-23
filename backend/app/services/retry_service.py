import logging
import time
from collections.abc import Callable
from typing import TypeVar


logger = logging.getLogger(__name__)

ResultT = TypeVar("ResultT")

TRANSIENT_ERROR_NUMBERS = {
    10035,
    10053,
    10054,
    10060,
}

TRANSIENT_ERROR_NAMES = {
    "ConnectError",
    "ConnectTimeout",
    "PoolTimeout",
    "ReadError",
    "ReadTimeout",
    "RemoteProtocolError",
    "WriteError",
    "WriteTimeout",
}

TRANSIENT_MESSAGE_PARTS = {
    "connection reset",
    "connection terminated",
    "operation has timed out",
    "pseudo-header in trailer",
    "server disconnected",
    "temporarily unavailable",
    "winerror 10035",
}


def retry_transient(
    operation: Callable[[], ResultT],
    *,
    operation_name: str,
    attempts: int = 3,
    initial_delay_seconds: float = 0.5,
) -> ResultT:
    if attempts < 1:
        raise ValueError(
            "Deneme sayısı en az 1 olmalıdır."
        )

    delay = initial_delay_seconds

    for attempt in range(1, attempts + 1):
        try:
            return operation()

        except Exception as exc:
            if (
                attempt == attempts
                or not is_transient_error(exc)
            ):
                raise

            logger.warning(
                "%s geçici ağ hatası nedeniyle "
                "yeniden denenecek (%s/%s): %r",
                operation_name,
                attempt,
                attempts,
                exc,
            )

            time.sleep(delay)
            delay *= 2

    raise RuntimeError(
        "Yeniden deneme döngüsü beklenmedik şekilde sonlandı."
    )


def is_transient_error(
    exception: BaseException,
) -> bool:
    for current in _walk_exception_chain(exception):
        error_number = (
            getattr(current, "winerror", None)
            or getattr(current, "errno", None)
        )

        if error_number in TRANSIENT_ERROR_NUMBERS:
            return True

        if (
            type(current).__name__
            in TRANSIENT_ERROR_NAMES
        ):
            return True

        message = str(current).lower()

        if any(
            part in message
            for part in TRANSIENT_MESSAGE_PARTS
        ):
            return True

    return False


def _walk_exception_chain(
    exception: BaseException,
) -> list[BaseException]:
    chain: list[BaseException] = []
    current: BaseException | None = exception
    visited: set[int] = set()

    while (
        current is not None
        and id(current) not in visited
    ):
        chain.append(current)
        visited.add(id(current))
        current = current.__cause__ or current.__context__

    return chain

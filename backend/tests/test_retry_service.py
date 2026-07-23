import pytest

from app.services.retry_service import (
    is_transient_error,
    retry_transient,
)


def test_retries_winerror_with_exponential_backoff(
    monkeypatch,
):
    calls = 0
    delays: list[float] = []

    def operation() -> str:
        nonlocal calls
        calls += 1

        if calls < 3:
            error = OSError(
                10035,
                "İşlem hemen tamamlanamadı.",
            )
            error.winerror = 10035
            raise error

        return "ok"

    monkeypatch.setattr(
        "app.services.retry_service.time.sleep",
        delays.append,
    )

    result = retry_transient(
        operation,
        operation_name="test",
    )

    assert result == "ok"
    assert calls == 3
    assert delays == [0.5, 1.0]


def test_does_not_retry_non_transient_error(
    monkeypatch,
):
    calls = 0
    delays: list[float] = []

    def operation() -> None:
        nonlocal calls
        calls += 1
        raise ValueError("Geçersiz veri")

    monkeypatch.setattr(
        "app.services.retry_service.time.sleep",
        delays.append,
    )

    with pytest.raises(ValueError):
        retry_transient(
            operation,
            operation_name="test",
        )

    assert calls == 1
    assert delays == []


def test_detects_transient_error_in_cause_chain():
    root = OSError(
        10060,
        "Bağlantı zaman aşımına uğradı.",
    )
    root.winerror = 10060

    wrapper = RuntimeError("Üst seviye hata")
    wrapper.__cause__ = root

    assert is_transient_error(wrapper) is True


def test_rejects_invalid_attempt_count():
    with pytest.raises(ValueError):
        retry_transient(
            lambda: None,
            operation_name="test",
            attempts=0,
        )

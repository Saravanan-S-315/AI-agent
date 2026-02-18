from app.main import run
from app.services import execute


def test_run_returns_success_code() -> None:
    assert run() == 0


def test_execute_rejects_negative_items() -> None:
    try:
        execute({'items': -1})
    except ValueError as exc:
        assert 'non-negative' in str(exc)
    else:
        raise AssertionError('expected ValueError')

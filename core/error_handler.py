"""
EduSense AI 360 - Central Error Handler
=======================================

A single place to contain, classify, log, and recover from faults, implementing
the architecture's rule: *no single fault crashes the application; degrade safely
and inform the user.*

Provides:
* :func:`handle` - log an exception (with context) and return a user-facing message.
* :func:`safe`   - a decorator that runs a callable, and on failure logs and
  returns a configured fallback instead of propagating.
* :class:`guard` - a context manager for the same behaviour around a block.

Expected domain faults (:class:`EduSenseError`) are logged at WARNING/ERROR with
their friendly message; unexpected exceptions are logged at ERROR with a full
traceback and treated as recoverable wherever a fallback is provided.
"""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional, TypeVar

from core.exceptions import EduSenseError
from core.logger import get_logger

T = TypeVar("T")

_log = get_logger("errors")


def handle(exc: BaseException, *, context: str = "", category: str = "errors") -> str:
    """Log an exception and return a user-facing message.

    Parameters
    ----------
    exc:
        The exception to handle.
    context:
        Short description of what was happening (e.g. "emotion prediction").
    category:
        Logger category to also record under (in addition to the error sink).
    """
    where = f" during {context}" if context else ""
    cat_log = get_logger(category)

    if isinstance(exc, EduSenseError):
        level = "warning" if exc.recoverable else "error"
        getattr(cat_log, level)("Handled %s%s: %s", type(exc).__name__, where, exc.message)
        return exc.user_message

    # Unexpected: capture full traceback for diagnosis.
    cat_log.error("Unexpected error%s: %s", where, exc, exc_info=True)
    _log.error("Unexpected error%s: %s", where, exc, exc_info=True)
    return "An unexpected error occurred. The application will continue."


def safe(
    fallback: Optional[T] = None,
    *,
    context: str = "",
    category: str = "errors",
    reraise: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """Decorator: run the function, and on error log and return ``fallback``.

    Use for per-frame or per-face operations that must never break the pipeline.
    Set ``reraise=True`` for call sites where the caller handles recovery itself.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - deliberate boundary catch
                ctx = context or func.__name__
                handle(exc, context=ctx, category=category)
                if reraise:
                    raise
                return fallback

        return wrapper

    return decorator


class guard:
    """Context manager that contains and logs exceptions in a block.

    Example
    -------
        with guard(context="loading model", category="ai"):
            model.load()
    """

    def __init__(self, *, context: str = "", category: str = "errors", reraise: bool = False) -> None:
        self.context = context
        self.category = category
        self.reraise = reraise
        self.error: Optional[BaseException] = None
        self.user_message: Optional[str] = None

    def __enter__(self) -> "guard":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc is None:
            return False
        self.error = exc
        self.user_message = handle(exc, context=self.context, category=self.category)
        return not self.reraise  # suppress unless asked to re-raise

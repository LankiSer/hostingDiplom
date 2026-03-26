import time
from collections.abc import Callable


class RetryPolicy:
    def __init__(self, max_attempts: int, base_delay_ms: int) -> None:
        self.base_delay_ms = base_delay_ms
        self.max_attempts = max_attempts

    def run(self, operation: Callable[[], str]) -> tuple[str, int]:
        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return operation(), attempt
            except OSError as error:
                last_error = error
                if attempt == self.max_attempts:
                    break
                time.sleep((self.base_delay_ms * attempt) / 1000)

        raise RuntimeError("Retry policy exhausted") from last_error

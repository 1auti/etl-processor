from typing import Any, Dict


class RetryStats:
    """Clase para registrar estadísticas de reintentos."""

    def __init__(self):
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
        self.total_wait_time = 0.0
        self.exceptions = {}

    def record_attempt(self, success: bool, wait_time: float = 0, exception: Exception = None):
        self.total_attempts += 1
        if success:
            self.successful_attempts += 1
        else:
            self.failed_attempts += 1
            self.total_wait_time += wait_time
            if exception:
                exc_name = type(exception).__name__
                self.exceptions[exc_name] = self.exceptions.get(exc_name, 0) + 1

    def get_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de las estadísticas."""
        return {
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "failed_attempts": self.failed_attempts,
            "success_rate": self.successful_attempts / max(1, self.total_attempts),
            "total_wait_time_seconds": self.total_wait_time,
            "exceptions": self.exceptions,
        }

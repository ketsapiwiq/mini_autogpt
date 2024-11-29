"""Error handling utilities for mini_autogpt."""

class ErrorCounter:
    """Global error counter to track consecutive failures."""
    _instance = None
    _fail_counter = 0
    MAX_FAILURES = 5

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorCounter, cls).__new__(cls)
        return cls._instance

    @classmethod
    def increment(cls):
        """Increment the failure counter."""
        cls._fail_counter += 1
        return cls._fail_counter

    @classmethod
    def reset(cls):
        """Reset the failure counter."""
        cls._fail_counter = 0

    @classmethod
    def get_count(cls):
        """Get current failure count."""
        return cls._fail_counter

    @classmethod
    def should_exit(cls):
        """Check if max failures reached."""
        return cls._fail_counter >= cls.MAX_FAILURES

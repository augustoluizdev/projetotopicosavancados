"""
Domain Exception: Event Not Found
Exception raised when an event is not found in the system.
"""


class EventNotFound(Exception):
    """Exception raised when an event is not found."""

    def __init__(self, event_id: str, message: str = None):
        self.event_id = event_id
        if message is None:
            message = f"Event with id '{event_id}' not found"
        super().__init__(message)
# This file contains the definition 'Event' object, 'event' function and 'EventTypes' enum.
from dataclasses import dataclass


class EventType:
    """Enum for event types."""

    # Event type for when a prompt is created
    PROMPT_CREATED = "PROMPT_CREATED"


@dataclass
class Event:
    event: str

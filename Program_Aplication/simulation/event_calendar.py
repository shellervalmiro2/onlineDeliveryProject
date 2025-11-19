from datetime import datetime, timedelta
import heapq
from typing import Callable, Any
from enum import Enum


class EventType(Enum):
    ORDER_ARRIVAL = "order_arrival"
    KITCHEN_COMPLETION = "kitchen_completion"
    STATISTICS_UPDATE = "statistics_update"
    SYSTEM_CHECK = "system_check"


class Event:
    def __init__(self, event_time: datetime, event_type: EventType,
                 data: Any = None, callback: Callable = None):
        self.event_time = event_time
        self.event_type = event_type
        self.data = data
        self.callback = callback

    def __lt__(self, other):
        return self.event_time < other.event_time


class EventCalendar:
    def __init__(self):
        self.events = []
        self.current_time = datetime.now()

    def add_event(self, event: Event):
        heapq.heappush(self.events, event)

    def get_next_event(self) -> Event:
        if self.events:
            return heapq.heappop(self.events)
        return None

    def peek_next_event(self) -> Event:
        if self.events:
            return self.events[0]
        return None

    def is_empty(self) -> bool:
        return len(self.events) == 0

    def clear(self):
        self.events = []
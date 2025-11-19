import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class OrderStatus(Enum):
    PENDING = "pending"
    COOKING = "cooking"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order:
    def __init__(self, source_id: int, items: list, address: str):
        self.order_id = str(uuid.uuid4())
        self.source_id = source_id
        self.order_time = datetime.now()
        self.status = OrderStatus.PENDING
        self.items = items
        self.address = address
        self.start_cooking_time: Optional[datetime] = None
        self.completion_time: Optional[datetime] = None

    def get_waiting_time(self) -> timedelta:
        if self.start_cooking_time:
            return self.start_cooking_time - self.order_time
        return datetime.now() - self.order_time

    def is_expired(self, max_wait_minutes: int = 15) -> bool:
        waiting_time = datetime.now() - self.order_time
        return waiting_time > timedelta(minutes=max_wait_minutes)

    def __str__(self):
        return f"Order {self.order_id[:8]} from Source {self.source_id}"
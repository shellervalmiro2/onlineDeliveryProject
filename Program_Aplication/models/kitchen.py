import random
from datetime import datetime, timedelta
from typing import Optional
from .order import Order, OrderStatus


class KitchenLine:
    def __init__(self, line_id: int, mean_service_time: float = 10.0):
        self.line_id = line_id
        self.is_busy = False
        self.current_order: Optional[Order] = None
        self.start_time: Optional[datetime] = None
        self.mean_service_time = mean_service_time

    def assign_order(self, order: Order) -> bool:
        if self.is_busy:
            return False

        self.current_order = order
        self.is_busy = True
        self.start_time = datetime.now()
        order.status = OrderStatus.COOKING
        order.start_cooking_time = self.start_time

        service_time = random.expovariate(1.0 / self.mean_service_time)
        self.completion_time = self.start_time + timedelta(minutes=service_time)
        return True

    def complete_order(self) -> Optional[Order]:
        if not self.is_busy or not self.current_order:
            return None

        completed_order = self.current_order
        completed_order.status = OrderStatus.COMPLETED
        completed_order.completion_time = datetime.now()

        self.current_order = None
        self.is_busy = False
        self.start_time = None
        self.completion_time = None

        return completed_order

    def get_remaining_time(self) -> Optional[timedelta]:
        if not self.completion_time:
            return None
        return max(timedelta(0), self.completion_time - datetime.now())

    def is_available(self) -> bool:
        return not self.is_busy

    def update_status(self, current_time: datetime) -> bool:
        if self.is_busy and self.completion_time and current_time >= self.completion_time:
            return True
        return False

    def __str__(self):
        status = "BUSY" if self.is_busy else "FREE"
        if self.is_busy and self.current_order:
            return f"Kitchen {self.line_id}: {status} - {self.current_order}"
        return f"Kitchen {self.line_id}: {status}"
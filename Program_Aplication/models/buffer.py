from typing import List, Optional, Tuple
from .order import Order


class BufferOperationResult:
    def __init__(self, success: bool, rejected_order: Optional[Order] = None,
                 message: str = "", insertion_position: int = -1):
        self.success = success
        self.rejected_order = rejected_order
        self.message = message
        self.insertion_position = insertion_position

    def __str__(self):
        return f"Success: {self.success}, Message: {self.message}"


class CircularBuffer:
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.buffer: List[Optional[Order]] = [None] * capacity
        self.pointer = 0
        self.oldest_pointer = 0
        self.count = 0

    def add_item(self, order: Order) -> BufferOperationResult:
        if self.is_full():
            oldest_order = self.remove_oldest_item()
            result = self._find_insertion_position()
            if result[0] != -1:
                self.buffer[result[0]] = order
                self.pointer = (result[0] + 1) % self.capacity
                self.count += 1
                return BufferOperationResult(
                    success=True,
                    rejected_order=oldest_order,
                    message="Buffer was full, oldest order rejected",
                    insertion_position=result[0]
                )
            return BufferOperationResult(False, message="Cannot find insertion position")
        else:
            result = self._find_insertion_position()
            if result[0] != -1:
                self.buffer[result[0]] = order
                self.pointer = (result[0] + 1) % self.capacity
                self.count += 1
                return BufferOperationResult(
                    success=True,
                    insertion_position=result[0],
                    message="Order added successfully"
                )
            return BufferOperationResult(False, message="Cannot find insertion position")

    def _find_insertion_position(self) -> Tuple[int, bool]:
        start = self.pointer
        current = start

        while True:
            if self.buffer[current] is None:
                return current, False
            current = (current + 1) % self.capacity
            if current == start:
                break

        return -1, True

    def get_oldest_item(self) -> Optional[Order]:
        if self.is_empty():
            return None

        oldest_order = None
        oldest_time = None

        for i in range(self.capacity):
            if self.buffer[i] is not None:
                if oldest_time is None or self.buffer[i].order_time < oldest_time:
                    oldest_time = self.buffer[i].order_time
                    oldest_order = self.buffer[i]

        return oldest_order

    def remove_oldest_item(self) -> Optional[Order]:
        if self.is_empty():
            return None

        oldest_order = None
        oldest_time = None
        oldest_index = -1

        for i in range(self.capacity):
            if self.buffer[i] is not None:
                if oldest_time is None or self.buffer[i].order_time < oldest_time:
                    oldest_time = self.buffer[i].order_time
                    oldest_order = self.buffer[i]
                    oldest_index = i

        if oldest_index != -1:
            self.buffer[oldest_index] = None
            self.count -= 1
            if not self.is_empty():
                self.oldest_pointer = self._find_next_oldest()
            else:
                self.oldest_pointer = 0

        return oldest_order

    def _find_next_oldest(self) -> int:
        oldest_index = -1
        oldest_time = None

        for i in range(self.capacity):
            if self.buffer[i] is not None:
                if oldest_time is None or self.buffer[i].order_time < oldest_time:
                    oldest_time = self.buffer[i].order_time
                    oldest_index = i

        return oldest_index if oldest_index != -1 else 0

    def is_full(self) -> bool:
        return self.count == self.capacity

    def is_empty(self) -> bool:
        return self.count == 0

    def get_buffer_state(self) -> List[Optional[Order]]:
        return self.buffer.copy()

    def __str__(self):
        status = []
        for i, order in enumerate(self.buffer):
            if order:
                status.append(f"[{i}: {order.order_id[:8]}]")
            else:
                status.append(f"[{i}: EMPTY]")
        return " | ".join(status)
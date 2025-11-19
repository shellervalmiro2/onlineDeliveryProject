from typing import List, Optional, Tuple
from datetime import datetime
from models.order import Order
from models.kitchen import KitchenLine
from models.buffer import CircularBuffer, BufferOperationResult


class DispatchResult:
    def __init__(self, dispatched: bool, assigned_kitchen: Optional[KitchenLine] = None,
                 error_message: str = ""):
        self.dispatched = dispatched
        self.assigned_kitchen = assigned_kitchen
        self.error_message = error_message


class RejectionResult:
    def __init__(self, handled: bool, cancelled_order: Optional[Order] = None,
                 new_order: Optional[Order] = None, error_message: str = ""):
        self.handled = handled
        self.cancelled_order = cancelled_order
        self.new_order = new_order
        self.error_message = error_message


class PlacementDispatcher:
    def __init__(self):
        self.stats = {"direct_to_device": 0, "to_buffer": 0, "rejections": 0}

    def process_incoming_order(self, order: Order, buffer: CircularBuffer,
                               kitchen_lines: List[KitchenLine]) -> Tuple[bool, Optional[KitchenLine]]:
        free_kitchen = self._find_first_free_kitchen(kitchen_lines)

        if free_kitchen is not None:
            if free_kitchen.assign_order(order):
                print(f"  Direct to kitchen {free_kitchen.line_id}")
                self.stats["direct_to_device"] += 1
                return True, free_kitchen

        print(f"  No free kitchens! All {len(kitchen_lines)} kitchens are busy.")
        print(f"  Trying to place in buffer... (currently {buffer.count}/{buffer.capacity} occupied)")

        buffer_result = buffer.add_item(order)

        if buffer_result.success:
            print(f"  Placed in buffer at position {buffer_result.insertion_position}")
            self.stats["to_buffer"] += 1
            return True, None
        else:
            print(f"  Buffer full! Capacity: {buffer.capacity}, Occupied: {buffer.count}")
            rejection_result = self._handle_buffer_full(order, buffer)

            if rejection_result.handled:
                print(f"  Replaced oldest order '{rejection_result.cancelled_order.order_id[:8]}' with new order")
                self.stats["rejections"] += 1
                return True, None
            else:
                print(f"  Order rejected completely - cannot handle buffer full situation")
                return False, None

    def _find_first_free_kitchen(self, kitchen_lines: List[KitchenLine]) -> Optional[KitchenLine]:
        for kitchen in kitchen_lines:
            if kitchen.is_available():
                return kitchen
        return None

    def _handle_buffer_full(self, new_order: Order, buffer: CircularBuffer) -> RejectionResult:
        if not buffer.is_full():
            return RejectionResult(False, error_message="Buffer is not full")

        rejected_order = buffer.remove_oldest_item()

        buffer_result = buffer.add_item(new_order)

        if buffer_result.success:
            return RejectionResult(True, cancelled_order=rejected_order, new_order=new_order)
        else:
            if rejected_order:
                buffer.add_item(rejected_order)
            return RejectionResult(False, error_message="Failed to handle buffer full")


class SelectionDispatcher:
    def __init__(self):
        self.stats = {"dispatched_from_buffer": 0, "kitchen_assignments": 0}

    def process_available_kitchens(self, buffer: CircularBuffer,
                                   kitchen_lines: List[KitchenLine]) -> List[Order]:
        completed_orders = []

        for kitchen in kitchen_lines:
            if kitchen.is_busy and kitchen.update_status(datetime.now()):
                completed_order = kitchen.complete_order()
                if completed_order:
                    completed_orders.append(completed_order)
                    self.stats["kitchen_assignments"] += 1

        for kitchen in kitchen_lines:
            if kitchen.is_available() and not buffer.is_empty():
                dispatch_result = self._dispatch_from_buffer(buffer, kitchen)
                if dispatch_result.dispatched:
                    self.stats["dispatched_from_buffer"] += 1

        return completed_orders

    def _dispatch_from_buffer(self, buffer: CircularBuffer,
                              kitchen: KitchenLine) -> DispatchResult:
        if buffer.is_empty():
            return DispatchResult(False, error_message="Buffer is empty")

        oldest_order = buffer.get_oldest_item()
        if oldest_order is None:
            return DispatchResult(False, error_message="No orders in buffer")

        if kitchen.assign_order(oldest_order):
            buffer.remove_oldest_item()
            return DispatchResult(True, assigned_kitchen=kitchen)

        return DispatchResult(False, error_message="Failed to assign order to kitchen")
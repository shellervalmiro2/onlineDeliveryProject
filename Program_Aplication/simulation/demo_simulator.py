import random
from datetime import datetime, timedelta
from models.order import Order
from models.kitchen import KitchenLine
from models.buffer import CircularBuffer
from models.dispatcher import PlacementDispatcher, SelectionDispatcher
from simulation.event_calendar import EventCalendar, EventType, Event
from statistics.stats_collector import StatisticsCollector


class DemoSimulator:
    def __init__(self):
        self.num_sources = 1
        self.num_kitchens = 2
        self.buffer_capacity = 3
        self.mean_arrival_time = 0.2
        self.mean_service_time = 10.0

        self.kitchen_lines = [KitchenLine(i, self.mean_service_time) for i in range(self.num_kitchens)]
        self.buffer = CircularBuffer(self.buffer_capacity)
        self.placement_dispatcher = PlacementDispatcher()
        self.selection_dispatcher = SelectionDispatcher()
        self.event_calendar = EventCalendar()
        self.stats_collector = StatisticsCollector()

        self.current_time = datetime.now()
        self.start_time = self.current_time
        self.step_count = 0
        self.total_orders_generated = 0

        self._generate_initial_events_burst()

    def _generate_initial_events_burst(self):
        print("Generating initial order burst to quickly fill system...")
        for i in range(8):
            arrival_time = self.current_time + timedelta(minutes=random.uniform(0, 0.5))
            self._schedule_order_arrival(0, arrival_time)

    def _schedule_order_arrival(self, source_id: int, arrival_time: datetime):
        self.event_calendar.add_event(Event(
            arrival_time,
            EventType.ORDER_ARRIVAL,
            {"source_id": source_id},
            self._handle_order_arrival
        ))

    def _generate_next_arrival_time(self, source_id: int) -> datetime:
        interval = random.uniform(0.1, 0.5)
        return self.current_time + timedelta(minutes=interval)

    def _handle_order_arrival(self, source_id: int):
        items = [f"Item_{random.randint(1, 10)}" for _ in range(random.randint(1, 3))]
        address = f"Address_{random.randint(1, 100)}"
        order = Order(source_id, items, address)

        self.total_orders_generated += 1
        self.stats_collector.record_order_arrival(order)

        print(f"SPECIAL EVENT: Order arrival - {order}")

        placed, assigned_kitchen = self.placement_dispatcher.process_incoming_order(
            order, self.buffer, self.kitchen_lines
        )

        if placed:
            if assigned_kitchen:
                print(f"  Direct to kitchen {assigned_kitchen.line_id}")
                self.stats_collector.record_order_dispatched(order, assigned_kitchen)
                self._schedule_kitchen_completion(assigned_kitchen)
            else:
                print(f"  Successfully placed in buffer (total in buffer: {self.buffer.count})")
                self.stats_collector.record_order_buffered(order)
        else:
            print(f"  ORDER REJECTED - system overloaded!")
            self.stats_collector.record_order_rejected(order)

        next_arrival = self._generate_next_arrival_time(source_id)
        self._schedule_order_arrival(source_id, next_arrival)

    def _schedule_kitchen_completion(self, kitchen: KitchenLine):
        if kitchen.completion_time:
            self.event_calendar.add_event(Event(
                kitchen.completion_time,
                EventType.KITCHEN_COMPLETION,
                kitchen,
                self._handle_kitchen_completion
            ))

    def _handle_kitchen_completion(self, kitchen: KitchenLine):
        print(f"SPECIAL EVENT: Kitchen {kitchen.line_id} completion")

        completed_order = kitchen.complete_order()
        if completed_order:
            print(f"  Order completed: {completed_order}")
            self.stats_collector.record_order_completed(completed_order)

        completed_orders = self.selection_dispatcher.process_available_kitchens(
            self.buffer, [kitchen]
        )

        if kitchen.is_busy:
            self._schedule_kitchen_completion(kitchen)
        else:
            print(f"  Kitchen {kitchen.line_id} now free, but buffer has {self.buffer.count} orders")

    def run_step(self) -> bool:
        if self.event_calendar.is_empty():
            print("No more events in calendar")
            return False

        next_event = self.event_calendar.get_next_event()
        self.current_time = next_event.event_time
        self.step_count += 1

        print(f"\n{'=' * 60}")
        print(f"STEP {self.step_count} - SPECIAL EVENT PROCESSING")
        print(f"Time: {self.current_time.strftime('%H:%M:%S')}")
        print(f"Event Type: {next_event.event_type.value}")
        print(f"{'=' * 60}")

        if next_event.callback:
            if next_event.event_type == EventType.ORDER_ARRIVAL:
                next_event.callback(**next_event.data)
            elif next_event.event_type == EventType.KITCHEN_COMPLETION:
                next_event.callback(next_event.data)

        self._update_system_state()
        return True

    def _update_system_state(self):
        busy_kitchens = sum(1 for k in self.kitchen_lines if k.is_busy)
        self.stats_collector.update_system_state(
            self.buffer.count,
            busy_kitchens,
            self.kitchen_lines
        )

        self._display_demo_state()

    def _display_demo_state(self):
        print(f"\nDEMO SYSTEM STATE (Step {self.step_count})")
        print(f"Current Time: {self.current_time.strftime('%H:%M:%S')}")

        print(f"\nKITCHENS ({self.num_kitchens}):")
        for kitchen in self.kitchen_lines:
            status = "FREE" if not kitchen.is_busy else "BUSY"
            if kitchen.is_busy:
                remaining = kitchen.get_remaining_time()
                rem_sec = max(0, remaining.total_seconds()) if remaining else 0
                print(f"  K{kitchen.line_id}: {status} - {rem_sec:.0f}s remaining")
            else:
                print(f"  K{kitchen.line_id}: {status}")

        print(f"\nBUFFER (Capacity: {self.buffer.capacity}):")
        print(f"  Occupied: {self.buffer.count}/{self.buffer.capacity}")
        print(f"  Insert Pointer: {self.buffer.pointer}")

        buffer_vis = []
        for i, order in enumerate(self.buffer.buffer):
            if order:
                buffer_vis.append(f"[{i}: {order.order_id[:4]}]")
            else:
                buffer_vis.append(f"[{i}: ----]")
        print("  " + " | ".join(buffer_vis))

        stats = self.stats_collector.get_current_stats()
        print(f"\nQUICK STATS:")
        print(f"  Total Orders: {stats['total_orders']}")
        print(f"  In Buffer: {self.buffer.count}")
        print(f"  Rejected: {stats['rejected_orders']}")

    def calculate_system_load(self) -> float:
        total_time = (self.current_time - self.start_time).total_seconds() / 60
        if total_time == 0:
            return 0.0

        input_intensity = self.total_orders_generated / total_time
        output_intensity = (self.stats_collector.completed_orders +
                            self.stats_collector.rejected_orders) / total_time

        return input_intensity / output_intensity if output_intensity > 0 else 0.0
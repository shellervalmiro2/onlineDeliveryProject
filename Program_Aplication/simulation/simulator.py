import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from models.order import Order
from models.kitchen import KitchenLine
from models.buffer import CircularBuffer
from models.dispatcher import PlacementDispatcher, SelectionDispatcher
from simulation.event_calendar import EventCalendar, EventType, Event
from statistics.stats_collector import StatisticsCollector


class SimulationMode:
    STEP_BY_STEP = "step_by_step"
    AUTOMATIC = "automatic"


class SpecialEventSimulator:
    def __init__(self, num_sources: int = 1, num_kitchens: int = 3,
                 buffer_capacity: int = 20, mean_arrival_time: float = 2.0,
                 mean_service_time: float = 10.0):

        self.num_sources = num_sources
        self.num_kitchens = num_kitchens
        self.buffer_capacity = buffer_capacity
        self.mean_arrival_time = mean_arrival_time
        self.mean_service_time = mean_service_time

        self.kitchen_lines = [KitchenLine(i, mean_service_time) for i in range(num_kitchens)]
        self.buffer = CircularBuffer(buffer_capacity)
        self.placement_dispatcher = PlacementDispatcher()
        self.selection_dispatcher = SelectionDispatcher()
        self.event_calendar = EventCalendar()
        self.stats_collector = StatisticsCollector()

        self.current_time = datetime.now()
        self.start_time = self.current_time
        self.is_running = False
        self.simulation_mode = SimulationMode.STEP_BY_STEP
        self.step_count = 0
        self.total_orders_generated = 0

        self._generate_initial_events()

    def _generate_initial_events(self):
        for source_id in range(self.num_sources):
            arrival_time = self.current_time + timedelta(minutes=random.uniform(0, 5))
            self._schedule_order_arrival(source_id, arrival_time)

    def _schedule_order_arrival(self, source_id: int, arrival_time: datetime):
        self.event_calendar.add_event(Event(
            arrival_time,
            EventType.ORDER_ARRIVAL,
            {"source_id": source_id},
            self._handle_order_arrival
        ))

    def _generate_next_arrival_time(self, source_id: int) -> datetime:
        min_time = max(0.1, self.mean_arrival_time - 1)
        max_time = self.mean_arrival_time + 1
        interval = random.uniform(min_time, max_time)
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
                print(f"  Placed in buffer (position: {self.buffer.count})")
                self.stats_collector.record_order_buffered(order)
        else:
            print(f"  Order rejected")
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

    def run_step(self) -> bool:
        if self.event_calendar.is_empty():
            print("No more events in calendar")
            return False

        next_event = self.event_calendar.get_next_event()
        self.current_time = next_event.event_time
        self.step_count += 1

        self._process_special_event(next_event)

        self._update_system_state()

        return True

    def _process_special_event(self, event: Event):
        print(f"\n{'=' * 60}")
        print(f"STEP {self.step_count} - SPECIAL EVENT PROCESSING")
        print(f"Time: {self.current_time.strftime('%H:%M:%S')}")
        print(f"Event Type: {event.event_type.value}")
        print(f"{'=' * 60}")

        if event.callback:
            if event.event_type == EventType.ORDER_ARRIVAL:
                event.callback(**event.data)
            elif event.event_type == EventType.KITCHEN_COMPLETION:
                event.callback(event.data)

    def _update_system_state(self):
        busy_kitchens = sum(1 for k in self.kitchen_lines if k.is_busy)
        self.stats_collector.update_system_state(
            self.buffer.count,
            busy_kitchens,
            self.kitchen_lines
        )

        self.display_current_state()

    def run_automatic(self, max_orders: int = 1000, target_precision: bool = True):
        print(f"\nAUTOMATIC SIMULATION STARTED")

        if target_precision:
            current_stats = self.stats_collector.get_current_stats()
            current_p = current_stats['rejection_rate']
            required_N = self.stats_collector.calculate_required_iterations(current_p)
            max_orders = max(max_orders, required_N)
            print(f"   Target precision: 10% with confidence 0.9")
            print(f"   Required iterations: {required_N}")

        orders_at_start = self.total_orders_generated
        start_time = self.current_time

        while (self.total_orders_generated < orders_at_start + max_orders and
               not self.event_calendar.is_empty()):
            if not self.run_step():
                break

            if self.total_orders_generated % 50 == 0:
                progress = (self.total_orders_generated - orders_at_start) / max_orders * 100
                print(
                    f"   Progress: {progress:.1f}% ({self.total_orders_generated - orders_at_start}/{max_orders} orders)")

        simulation_time = (self.current_time - start_time).total_seconds() / 60
        system_load = self.calculate_system_load()

        print(f"\nAUTOMATIC SIMULATION COMPLETED")
        print(f"   Total orders processed: {self.total_orders_generated - orders_at_start}")
        print(f"   Simulation time: {simulation_time:.1f} minutes")
        print(f"   Final system load (ρ): {system_load:.3f}")

        if system_load > 1.2:
            print("   System is OVERLOADED (ρ > 1.2)")
        elif system_load < 0.8:
            print("   System is UNDERLOADED (ρ < 0.8)")
        else:
            print("   System is OPTIMALLY LOADED (0.8 ≤ ρ ≤ 1.2)")

    def display_current_state(self):
        print(f"\nSYSTEM STATE AFTER STEP {self.step_count}")
        print(f"Current Time: {self.current_time.strftime('%H:%M:%S')}")

        self._display_event_calendar()
        self._display_kitchens_state()
        self._display_buffer_state()
        self._display_statistics()

    def _display_event_calendar(self):
        print(f"\nEVENT CALENDAR (next 5 events):")
        events_to_show = sorted(self.event_calendar.events)[:5]
        for i, event in enumerate(events_to_show):
            time_str = event.event_time.strftime('%H:%M:%S')
            print(f"  {i + 1}. {time_str} - {event.event_type.value}")

    def _display_kitchens_state(self):
        print(f"\nKITCHEN LINES:")
        for kitchen in self.kitchen_lines:
            status = "FREE" if not kitchen.is_busy else "BUSY"
            if kitchen.is_busy and kitchen.current_order:
                remaining = kitchen.get_remaining_time()
                if remaining:
                    rem_sec = max(0, remaining.total_seconds())
                    print(f"  K{kitchen.line_id}: {status} - {kitchen.current_order.order_id[:8]} "
                          f"({rem_sec:.0f}s)")
            else:
                print(f"  K{kitchen.line_id}: {status}")

    def _display_buffer_state(self):
        print(f"\nBUFFER STATE:")
        print(f"  Capacity: {self.buffer.capacity}")
        print(f"  Occupied: {self.buffer.count}/{self.buffer.capacity}")
        print(f"  Insert Pointer: {self.buffer.pointer}")
        print(f"  Oldest Pointer: {self.buffer.oldest_pointer}")
        print(f"  Buffer: {self.buffer}")

    def _display_statistics(self):
        try:
            stats = self.stats_collector.get_current_stats()
            print(f"\nCURRENT STATISTICS:")
            print(f"  Total Orders: {stats['total_orders']}")
            print(f"  Completed: {stats['completed_orders']}")
            print(f"  In Buffer: {stats['buffered_orders']}")
            print(f"  Rejected: {stats['rejected_orders']}")
            print(f"  Kitchen Utilization: {stats.get('kitchen_utilization', 0):.1%}")
            print(f"  Buffer Utilization: {stats.get('buffer_utilization', 0):.1%}")
            print(f"  Rejection Rate: {stats.get('rejection_rate', 0):.1%}")
            print(f"  Avg Wait Time: {stats.get('avg_wait_time', 0):.1f} min")
        except Exception as e:
            print(f"\nError displaying statistics: {e}")
            print("  Statistics temporarily unavailable")

    def calculate_system_load(self) -> float:
        total_time = (self.current_time - self.start_time).total_seconds() / 60

        if total_time == 0:
            return 0.0

        input_intensity = self.total_orders_generated / total_time

        output_intensity = (self.stats_collector.completed_orders +
                            self.stats_collector.rejected_orders) / total_time

        if output_intensity == 0:
            return 0.0

        return input_intensity / output_intensity
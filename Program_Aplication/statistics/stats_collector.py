from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models.order import Order
from models.kitchen import KitchenLine


class SourceStatistics:
    def __init__(self, source_id: int):
        self.source_id = source_id
        self.generated_orders = 0
        self.completed_orders = 0
        self.rejected_orders = 0
        self.buffered_orders = 0
        self.total_wait_time = timedelta(0)
        self.total_service_time = timedelta(0)
        self.wait_times: List[float] = []
        self.service_times: List[float] = []


class StatisticsCollector:
    def __init__(self):
        self.start_time = datetime.now()
        self.sources: Dict[int, SourceStatistics] = {}

        self.kitchen_busy_time = [timedelta(0) for _ in range(10)]
        self.last_update_time = self.start_time
        self.kitchen_states = [False] * 10

        self.total_orders = 0
        self.completed_orders = 0
        self.rejected_orders = 0
        self.buffered_orders = 0

        self.utilization_history: List[float] = []
        self.buffer_usage_history: List[int] = []
        self.wait_time_history: List[float] = []
        self.rejection_history: List[int] = []
        self.load_history: List[float] = []
        self.timestamps: List[datetime] = []

    def _get_source_stats(self, source_id: int) -> SourceStatistics:
        if source_id not in self.sources:
            self.sources[source_id] = SourceStatistics(source_id)
        return self.sources[source_id]

    def record_order_arrival(self, order: Order):
        self.total_orders += 1
        source_stats = self._get_source_stats(order.source_id)
        source_stats.generated_orders += 1

    def record_order_dispatched(self, order: Order, kitchen: KitchenLine):
        self.record_order_arrival(order)

    def record_order_buffered(self, order: Order):
        self.buffered_orders += 1
        source_stats = self._get_source_stats(order.source_id)
        source_stats.buffered_orders += 1

    def record_order_completed(self, order: Order):
        self.completed_orders += 1
        source_stats = self._get_source_stats(order.source_id)
        source_stats.completed_orders += 1

        if order.start_cooking_time and order.completion_time:
            wait_time = order.start_cooking_time - order.order_time
            service_time = order.completion_time - order.start_cooking_time

            source_stats.total_wait_time += wait_time
            source_stats.total_service_time += service_time
            source_stats.wait_times.append(wait_time.total_seconds() / 60)
            source_stats.service_times.append(service_time.total_seconds() / 60)

    def record_order_rejected(self, order: Order):
        self.rejected_orders += 1
        source_stats = self._get_source_stats(order.source_id)
        source_stats.rejected_orders += 1

    def update_system_state(self, buffer_occupancy: int, busy_kitchens: int,
                            kitchen_lines: List[KitchenLine]):
        current_time = datetime.now()
        time_delta = current_time - self.last_update_time

        for i, kitchen in enumerate(kitchen_lines):
            if i < len(self.kitchen_states):
                if kitchen.is_busy:
                    self.kitchen_busy_time[i] += time_delta
                self.kitchen_states[i] = kitchen.is_busy

        self.last_update_time = current_time

        self.timestamps.append(current_time)
        self.buffer_usage_history.append(buffer_occupancy)

        current_utilization = busy_kitchens / len(kitchen_lines) if kitchen_lines else 0
        self.utilization_history.append(current_utilization)

        if self.completed_orders > 0:
            avg_wait = sum(stats.total_wait_time.total_seconds() / 60
                           for stats in self.sources.values()) / self.completed_orders
            self.wait_time_history.append(avg_wait)
        else:
            self.wait_time_history.append(0)

        self.rejection_history.append(self.rejected_orders)

    def get_current_stats(self) -> Dict[str, Any]:
        total_time = datetime.now() - self.start_time
        total_seconds = max(1, total_time.total_seconds())

        kitchen_utilization = 0.0
        if total_seconds > 0:
            total_busy_seconds = 0.0
            for busy_time in self.kitchen_busy_time:
                total_busy_seconds += busy_time.total_seconds()
            kitchen_utilization = total_busy_seconds / (len(self.kitchen_busy_time) * total_seconds)

        avg_wait_time = 0
        if self.completed_orders > 0:
            total_wait_seconds = sum(stats.total_wait_time.total_seconds()
                                     for stats in self.sources.values())
            avg_wait_time = total_wait_seconds / 60 / self.completed_orders

        buffer_utilization = 0.0
        if self.buffer_usage_history:
            buffer_utilization = self.buffer_usage_history[-1] / 20.0

        rejection_rate = self.rejected_orders / max(1, self.total_orders)

        total_minutes = total_seconds / 60
        orders_per_minute = self.total_orders / max(1, total_minutes)

        return {
            "total_orders": self.total_orders,
            "completed_orders": self.completed_orders,
            "rejected_orders": self.rejected_orders,
            "buffered_orders": self.buffered_orders,
            "kitchen_utilization": kitchen_utilization,
            "buffer_utilization": buffer_utilization,
            "avg_wait_time": avg_wait_time,
            "rejection_rate": rejection_rate,
            "orders_per_minute": orders_per_minute
        }

    def generate_final_report(self, system_load: float) -> Dict[str, Any]:
        print("\n" + "=" * 80)
        print("FINAL SIMULATION REPORT - TABLE 1: SOURCE CHARACTERISTICS")
        print("=" * 80)
        print(f"{'Source':<8} {'Generated':<10} {'P_reject':<10} {'T_system':<10} {'T_wait':<10} {'T_service':<10} {'D_wait':<10} {'D_service':<10}")
        print("-" * 80)

        source_reports = {}

        for source_id, stats in sorted(self.sources.items()):
            p_reject = stats.rejected_orders / max(1, stats.generated_orders)

            t_system = 0
            if stats.completed_orders > 0:
                total_system_time = stats.total_wait_time + stats.total_service_time
                t_system = total_system_time.total_seconds() / 60 / stats.completed_orders

            t_wait = 0
            if stats.completed_orders > 0:
                t_wait = stats.total_wait_time.total_seconds() / 60 / stats.completed_orders

            t_service = 0
            if stats.completed_orders > 0:
                t_service = stats.total_service_time.total_seconds() / 60 / stats.completed_orders

            d_wait = self._calculate_variance(stats.wait_times) if stats.wait_times else 0
            d_service = self._calculate_variance(stats.service_times) if stats.service_times else 0

            print(f"{f'S{source_id}':<8} {stats.generated_orders:<10} {p_reject:<10.3f} "
                  f"{t_system:<10.2f} {t_wait:<10.2f} {t_service:<10.2f} "
                  f"{d_wait:<10.2f} {d_service:<10.2f}")

            source_reports[source_id] = {
                'generated': stats.generated_orders,
                'p_reject': p_reject,
                't_system': t_system,
                't_wait': t_wait,
                't_service': t_service,
                'd_wait': d_wait,
                'd_service': d_service
            }

        print("\n" + "=" * 50)
        print("TABLE 2: KITCHEN UTILIZATION")
        print("=" * 50)
        print(f"{'Kitchen':<10} {'Utilization':<12}")
        print("-" * 25)

        total_time = (datetime.now() - self.start_time).total_seconds()
        kitchen_reports = {}

        for i, busy_time in enumerate(self.kitchen_busy_time):
            if i < len(self.kitchen_states):
                utilization = busy_time.total_seconds() / total_time if total_time > 0 else 0
                print(f"{f'K{i}':<10} {utilization:<12.3f}")
                kitchen_reports[i] = utilization

        print(f"\nSYSTEM LOAD (ρ): {system_load:.3f}")

        return {
            'sources': source_reports,
            'kitchens': kitchen_reports,
            'system_load': system_load
        }

    def _calculate_variance(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance

    def calculate_required_iterations(self, current_p: float, alpha: float = 0.9,
                                      delta: float = 0.1) -> int:
        if current_p == 0:
            return 1000

        t_alpha = 1.643

        N = (t_alpha ** 2 * (1 - current_p)) / (current_p * delta ** 2)
        return max(100, int(N))
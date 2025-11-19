from datetime import datetime
from typing import List, Optional
from ..models.order import Order
from ..models.kitchen import KitchenLine
from ..models.buffer import CircularBuffer


class ConsoleDisplay:
    """Класс для отображения состояния системы в консоли"""

    def __init__(self):
        self.display_width = 80

    def display_system_scheme(self, kitchen_lines: List[KitchenLine],
                              buffer: CircularBuffer, current_time: datetime,
                              step_count: int, event_description: str = ""):
        """
        Отображение формализованной схемы модели с текущим состоянием
        """
        print("\n" + "=" * self.display_width)
        print("ФОРМАЛИЗОВАННАЯ СХЕМА МОДЕЛИ ВС - ТЕКУЩЕЕ СОСТОЯНИЕ")
        print("=" * self.display_width)

        self._display_header(current_time, step_count, event_description)
        self._display_sources_section()
        self._display_placement_dispatcher()
        self._display_buffer_section(buffer)
        self._display_selection_dispatcher()
        self._display_kitchens_section(kitchen_lines)

        print("─" * self.display_width)

    def _display_header(self, current_time: datetime, step_count: int, event_description: str):
        """Отображение заголовка с временем и информацией о шаге"""
        time_str = current_time.strftime('%H:%M:%S')
        print(f"Шаг моделирования: {step_count} | Время: {time_str}")
        if event_description:
            print(f"Обрабатываемое событие: {event_description}")
        print()

    def _display_sources_section(self):
        """Отображение секции источников"""
        print("ИСТОЧНИКИ (ИБ - бесконечный)")
        print("   ┌─────────────┐")
        print("   │ Источник S0 │───┐")
        print("   └─────────────┘   │")
        print("                     ▼")

    def _display_placement_dispatcher(self):
        """Отображение диспетчера постановки"""
        print("ДИСПЕТЧЕР ПОСТАНОВКИ (ДП)")
        print("   ┌─────────────────────────────────┐")
        print("   │ Д2П2: первый свободный прибор   │")
        print("   │ Д10O3: выбивание старого заказа │")
        print("   └────────────────┬────────────────┘")
        print("                    │")
        print("        ┌───────────┼───────────┐")
        print("        ▼                       ▼")

    def _display_buffer_section(self, buffer: CircularBuffer):
        """Отображение секции буфера с указателями"""
        print("БУФЕРНАЯ ПАМЯТЬ (Д1031 - по кольцу)")
        print(f"   Емкость: {buffer.capacity} | Занято: {buffer.count}")

        print(f"   Указатель вставки: {buffer.pointer}")
        print(f"   Указатель извлечения: {buffer.oldest_pointer}")

        self._display_buffer_visualization(buffer)
        print("                                    │")
        print("                                    ▼")

    def _display_buffer_visualization(self, buffer: CircularBuffer):
        """Визуализация состояния буфера"""
        buffer_display = []
        for i, order in enumerate(buffer.buffer):
            if order is None:
                buffer_display.append(f"[{i:2d}: ────]")
            else:
                buffer_display.append(f"[{i:2d}: {order.order_id[:4]}]")

        print("   ┌" + "─" * 58 + "┐")
        for i in range(0, len(buffer_display), 5):
            line = buffer_display[i:i + 5]
            print("   │ " + " ".join(line) + " " * (58 - len(" ".join(line))) + "│")
        print("   └" + "─" * 58 + "┘")

    def _display_selection_dispatcher(self):
        """Отображение диспетчера выбора"""
        print("ДИСПЕТЧЕР ВЫБОРА (ДВ)")
        print("   ┌─────────────────────────────┐")
        print("   │ Д2Б2: FIFO - первый пришел, │")
        print("   │      первый обслужен        │")
        print("   └─────────────┬───────────────┘")
        print("                 ▼")

    def _display_kitchens_section(self, kitchen_lines: List[KitchenLine]):
        """Отображение секции приборов"""
        print("ОБСЛУЖИВАЮЩИЕ ПРИБОРЫ (П31 - экспоненциальное время)")
        print("   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐")

        status_line = ""
        for kitchen in kitchen_lines:
            status = "ЗАНЯТ" if kitchen.is_busy else "СВОБОДЕН"
            status_line += f"│ {status:^11} │  "
        print("   " + status_line)

        numbers_line = ""
        for kitchen in kitchen_lines:
            numbers_line += f"│ Прибор K{kitchen.line_id:^5} │  "
        print("   " + numbers_line)

        orders_line = ""
        for kitchen in kitchen_lines:
            if kitchen.is_busy and kitchen.current_order:
                order_id = kitchen.current_order.order_id[:6]
                orders_line += f"│ {order_id:^11} │  "
            else:
                orders_line += f"│ {'─':^11} │  "
        print("   " + orders_line)

        print("   └─────────────┘  └─────────────┘  └─────────────┘")

    def display_event_calendar(self, events, max_display: int = 5):
        """Отображение календаря событий"""
        if not events:
            print("Календарь событий: ПУСТ")
            return

        print(f"\nКАЛЕНДАРЬ СОБЫТИЙ (следующие {max_display}):")
        print("─" * 60)
        print(f"{'№':<3} {'Время':<12} {'Тип события':<25} {'Данные':<20}")
        print("─" * 60)

        sorted_events = sorted(events)[:max_display]
        for i, event in enumerate(sorted_events, 1):
            time_str = event.event_time.strftime('%H:%M:%S')
            event_type = self._format_event_type(event.event_type)
            data_str = self._format_event_data(event.data)

            print(f"{i:<3} {time_str:<12} {event_type:<25} {data_str:<20}")

    def _format_event_type(self, event_type) -> str:
        """Форматирование типа события для отображения"""
        event_names = {
            'order_arrival': 'Прибытие заказа',
            'kitchen_completion': 'Завершение прибора',
            'statistics_update': 'Обновление статистики',
            'system_check': 'Проверка системы'
        }
        return event_names.get(event_type.value, event_type.value)

    def _format_event_data(self, data) -> str:
        """Форматирование данных события для отображения"""
        if isinstance(data, dict) and 'source_id' in data:
            return f"Источник {data['source_id']}"
        elif hasattr(data, 'line_id'):
            return f"Прибор {data.line_id}"
        else:
            return str(data)[:18] + "..." if len(str(data)) > 18 else str(data)

    def display_detailed_statistics(self, stats: dict, system_load: float):
        """Детальное отображение статистики"""
        print("\nДЕТАЛЬНАЯ СТАТИСТИКА СИСТЕМЫ")
        print("─" * 60)

        print(f"Общая загрузка системы (ρ): {system_load:.3f}")
        print()

        print("ОСНОВНЫЕ МЕТРИКИ:")
        print(f"  • Всего заказов: {stats['total_orders']}")
        print(f"  • Обслужено: {stats['completed_orders']}")
        print(f"  • В буфере: {stats['buffered_orders']}")
        print(f"  • Отказов: {stats['rejected_orders']}")
        print(f"  • Вероятность отказа: {stats['rejection_rate']:.1%}")
        print()

        print("ВРЕМЕННЫЕ ХАРАКТЕРИСТИКИ:")
        print(f"  • Среднее время ожидания: {stats['avg_wait_time']:.1f} мин")
        print(f"  • Загрузка приборов: {stats['kitchen_utilization']:.1%}")
        print(f"  • Загрузка буфера: {stats['buffer_utilization']:.1%}")
        print()

        print("ПРОИЗВОДИТЕЛЬНОСТЬ:")
        print(f"  • Заказов в минуту: {stats['orders_per_minute']:.2f}")

    def display_step_summary(self, step_info: dict):
        """Отображение сводки по шагу"""
        print(f"\nСВОДКА ШАГА {step_info['step']}:")
        print("─" * 40)

        if step_info.get('order_arrived'):
            print(f"Прибыл заказ: {step_info['order_arrived']}")

        if step_info.get('order_completed'):
            print(f"Завершен заказ: {step_info['order_completed']}")

        if step_info.get('order_rejected'):
            print(f"Отклонен заказ: {step_info['order_rejected']}")

        if step_info.get('order_dispatched'):
            print(f"Заказ отправлен на прибор: {step_info['order_dispatched']}")

        if step_info.get('buffer_operation'):
            print(f"Операция с буфером: {step_info['buffer_operation']}")

    def display_waveform_diagram(self, events_history: list, time_period: int = 10):
        """
        Отображение временной диаграммы (Waveform)
        """
        print("\nВРЕМЕННАЯ ДИАГРАММА (Waveform)")
        print("─" * 70)

        if not events_history:
            print("История событий пуста")
            return

        time_slots = {}
        for event in events_history[-time_period:]:
            time_key = event['time'].strftime('%H:%M:%S')
            if time_key not in time_slots:
                time_slots[time_key] = []
            time_slots[time_key].append(event)

        print(f"{'Время':<10} {'События':<50}")
        print("─" * 70)

        for time_key in sorted(time_slots.keys()):
            events_str = ", ".join([self._format_waveform_event(e) for e in time_slots[time_key]])
            print(f"{time_key:<10} {events_str:<50}")

    def _format_waveform_event(self, event: dict) -> str:
        """Форматирование события для временной диаграммы"""
        event_type = event.get('type', '')
        order_id = event.get('order_id', '')[:4]

        symbols = {
            'order_arrival': f'Вход{order_id}',
            'kitchen_start': f'Начало{order_id}',
            'kitchen_complete': f'Готов{order_id}',
            'buffer_add': f'Буфер{order_id}',
            'buffer_remove': f'Выбор{order_id}',
            'rejection': f'Отказ{order_id}'
        }

        return symbols.get(event_type, event_type)

    def display_help(self):
        """Отображение справки по управлению"""
        print("\nУПРАВЛЕНИЕ СИМУЛЯЦИЕЙ")
        print("─" * 50)
        print("Пошаговый режим:")
        print("  [Enter] - следующий шаг")
        print("  [q]     - выход из режима")
        print("  [s]     - показать статистику")
        print("  [c]     - показать календарь событий")
        print("  [w]     - показать временную диаграмму")
        print()
        print("Автоматический режим:")
        print("  Укажите количество заказов для генерации")
        print("  Система автоматически достигнет требуемой точности")

    def clear_screen(self):
        """Очистка экрана (кроссплатформенная)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
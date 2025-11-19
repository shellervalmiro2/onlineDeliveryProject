import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simulator import SpecialEventSimulator, SimulationMode


def main():
    print("RESTAURANT DELIVERY ORDER PROCESSING SIMULATION")
    print("IEEE Std 610.12-1990 - Special Events Method")
    print("=" * 60)

    simulator = SpecialEventSimulator(
        num_sources=1,
        num_kitchens=2,
        buffer_capacity=5,
        mean_arrival_time=1.0,
        mean_service_time=8.0
    )

    while True:
        print("\nSIMULATION CONTROL PANEL")
        print("1. Step-by-step mode (Special Events)")
        print("2. Automatic mode with precision control")
        print("3. System parameters configuration")
        print("4. Display current state")
        print("5. Generate final report")
        print("6. Calculate required iterations")
        print("7. Demo scenario (buffer usage)")
        print("8. Exit")

        choice = input("\nSelect option (1-8): ").strip()

        if choice == "1":
            run_step_by_step(simulator)

        elif choice == "2":
            run_automatic_mode(simulator)

        elif choice == "3":
            configure_parameters(simulator)

        elif choice == "4":
            display_current_state(simulator)

        elif choice == "5":
            generate_final_report(simulator)

        elif choice == "6":
            calculate_precision(simulator)

        elif choice == "7":
            run_demo_scenario()

        elif choice == "8":
            print("Thank you for using the Restaurant SMO Simulator!")
            print("IEEE Std 610.12-1990 compliant - Special Events Method")
            break

        else:
            print("Invalid option, please try again")


def run_step_by_step(simulator):
    print("\nSTEP-BY-STEP MODE (Special Events Method)")
    print("Each step processes one special event")
    print("Press Enter to continue, 'q' to quit")

    step_count = 0
    max_steps = input("Enter maximum number of steps (default 20): ").strip()
    try:
        max_steps = int(max_steps) if max_steps else 20
    except ValueError:
        max_steps = 20
        print("Invalid input, using default 20 steps")

    while step_count < max_steps:
        step_count += 1
        if not simulator.run_step():
            print("No more events in calendar")
            break

        if step_count >= max_steps:
            print(f"\nStep limit reached ({max_steps} steps)")
            break

        user_input = input("\nPress Enter for next event or 'q' to quit: ")
        if user_input.lower() == 'q':
            break


def run_automatic_mode(simulator):
    print("\nAUTOMATIC MODE WITH PRECISION CONTROL")

    print("\nPRECISION OPTIONS:")
    print("1. Run with fixed number of orders")
    print("2. Run until required precision is achieved")

    precision_choice = input("Select option (1-2): ").strip()

    if precision_choice == "1":
        max_orders = input("Enter number of orders to generate (default 100): ").strip()
        try:
            max_orders = int(max_orders) if max_orders else 100
        except ValueError:
            max_orders = 100
            print("Invalid input, using default 100 orders")

        simulator.run_automatic(max_orders, target_precision=False)

    elif precision_choice == "2":
        current_stats = simulator.stats_collector.get_current_stats()
        current_p = current_stats['rejection_rate']
        required_N = simulator.stats_collector.calculate_required_iterations(current_p)

        print(f"\nPRECISION CALCULATION:")
        print(f"   Current rejection rate: {current_p:.3f}")
        print(f"   Required iterations for 10% precision: {required_N}")
        print(f"   Current total orders: {simulator.total_orders_generated}")

        if simulator.total_orders_generated >= required_N:
            print("Already achieved required precision!")
            return

        additional_orders = required_N - simulator.total_orders_generated
        print(f"   Additional orders needed: {additional_orders}")

        confirm = input(f"\nGenerate {additional_orders} additional orders? (y/n): ").strip().lower()
        if confirm == 'y':
            simulator.run_automatic(additional_orders, target_precision=True)
        else:
            print("Precision mode cancelled")

    else:
        print("Invalid option, returning to main menu")


def configure_parameters(simulator):
    print("\nSYSTEM PARAMETERS CONFIGURATION")
    print("Current configuration:")
    print(f"  Sources: {simulator.num_sources}")
    print(f"  Kitchens: {simulator.num_kitchens}")
    print(f"  Buffer capacity: {simulator.buffer_capacity}")
    print(f"  Mean arrival time: {simulator.mean_arrival_time} min")
    print(f"  Mean service time: {simulator.mean_service_time} min")

    print("\nNote: Changing parameters will reset the simulation!")
    confirm = input("Do you want to change parameters? (y/n): ").strip().lower()

    if confirm != 'y':
        return

    try:
        print("\nNEW PARAMETERS (press Enter to keep current value):")

        kitchens = input(f"Number of kitchens (current: {simulator.num_kitchens}): ").strip()
        if kitchens:
            simulator.num_kitchens = int(kitchens)

        buffer_cap = input(f"Buffer capacity (current: {simulator.buffer_capacity}): ").strip()
        if buffer_cap:
            simulator.buffer_capacity = int(buffer_cap)

        arrival_time = input(f"Mean arrival time in minutes (current: {simulator.mean_arrival_time}): ").strip()
        if arrival_time:
            simulator.mean_arrival_time = float(arrival_time)

        service_time = input(f"Mean service time in minutes (current: {simulator.mean_service_time}): ").strip()
        if service_time:
            simulator.mean_service_time = float(service_time)

        from simulation.simulator import SpecialEventSimulator
        new_simulator = SpecialEventSimulator(
            num_sources=simulator.num_sources,
            num_kitchens=simulator.num_kitchens,
            buffer_capacity=simulator.buffer_capacity,
            mean_arrival_time=simulator.mean_arrival_time,
            mean_service_time=simulator.mean_service_time
        )

        simulator.__dict__.update(new_simulator.__dict__)

        print("Parameters updated successfully! Simulation reset.")

    except ValueError as e:
        print(f"Invalid input: {e}")
        print("Parameters not changed")


def display_current_state(simulator):
    print("\nCURRENT SYSTEM STATE")
    print("=" * 50)
    simulator.display_current_state()


def generate_final_report(simulator):
    print("\nGENERATING FINAL REPORT")
    system_load = simulator.calculate_system_load()
    simulator.stats_collector.generate_final_report(system_load)

    print("\nSYSTEM ANALYSIS:")
    if system_load > 1.2:
        print("   System is OVERLOADED (ρ > 1.2)")
        print("   Recommendations:")
        print("   - Increase number of kitchens")
        print("   - Increase buffer capacity")
        print("   - Reduce arrival rate")
    elif system_load < 0.8:
        print("   System is UNDERLOADED (ρ < 0.8)")
        print("   Recommendations:")
        print("   - Reduce number of kitchens")
        print("   - Increase arrival rate")
    else:
        print("   System is OPTIMALLY LOADED (0.8 ≤ ρ ≤ 1.2)")
        print("   - Good balance between resources and demand")


def calculate_precision(simulator):
    print("\nPRECISION CALCULATION")
    current_stats = simulator.stats_collector.get_current_stats()
    current_p = current_stats['rejection_rate']
    required_N = simulator.stats_collector.calculate_required_iterations(current_p)

    print(f"Current rejection probability: {current_p:.3f}")
    print(f"Required iterations for 10% precision: {required_N}")
    print(f"Current total orders: {simulator.total_orders_generated}")

    if simulator.total_orders_generated >= required_N:
        print("Required precision already achieved!")
        additional_needed = 0
    else:
        additional_needed = required_N - simulator.total_orders_generated
        print(f"Additional orders needed: {additional_needed}")

    if simulator.total_orders_generated > 0:
        total_time_minutes = (simulator.current_time - simulator.start_time).total_seconds() / 60
        orders_per_minute = simulator.total_orders_generated / max(1, total_time_minutes)
        if additional_needed > 0 and orders_per_minute > 0:
            estimated_time = additional_needed / orders_per_minute
            print(f"Estimated time to achieve precision: {estimated_time:.1f} minutes")


def run_demo_scenario():
    print("\nDEMO SCENARIO: Testing Buffer Usage and Rejections")
    print("=" * 60)

    from simulation.demo_simulator import DemoSimulator
    demo_simulator = DemoSimulator()

    print("Demo parameters:")
    print("  - 1 source")
    print("  - 2 kitchen lines")
    print("  - Buffer capacity: 3")
    print("  - VERY HIGH order frequency (every 0.1-0.5 min)")
    print("  - Service time: 10 min")
    print("\nThis configuration will DEMONSTRATE:")
    print("  - Buffer usage when kitchens are busy")
    print("  - Order rejections when buffer is full")
    print("  - Special events processing")
    print("  - Circular buffer pointer movement")

    demo_steps = input("\nEnter number of demo steps (default 15): ").strip()
    try:
        demo_steps = int(demo_steps) if demo_steps else 15
    except ValueError:
        demo_steps = 15

    input("\nPress Enter to start aggressive demo...")

    print("\n" + "=" * 60)
    print("STARTING AGGRESSIVE DEMO SCENARIO")
    print("=" * 60)

    for step in range(demo_steps):
        print(f"\n--- Demo Step {step + 1}/{demo_steps} ---")
        if not demo_simulator.run_step():
            print("No more events in calendar")
            break

        if (step + 1) % 5 == 0:
            input(f"\nDemo paused at step {step + 1}. Press Enter to continue...")

    print("\n" + "=" * 60)
    print("DEMO COMPLETED - FINAL RESULTS")
    print("=" * 60)

    system_load = demo_simulator.calculate_system_load()
    demo_simulator.stats_collector.generate_final_report(system_load)

    print("\nDEMO ANALYSIS:")
    total_orders = demo_simulator.total_orders_generated
    rejected_orders = demo_simulator.stats_collector.rejected_orders
    buffer_usage = max(
        demo_simulator.stats_collector.buffer_usage_history) if demo_simulator.stats_collector.buffer_usage_history else 0

    print(f"  Total orders generated: {total_orders}")
    print(f"  Orders rejected: {rejected_orders}")
    print(f"  Maximum buffer usage: {buffer_usage}/3")
    print(f"  System load (ρ): {system_load:.3f}")

    if rejected_orders > 0:
        print("  Successfully demonstrated order rejections!")
    else:
        print("  No order rejections - system handled the load")

    if buffer_usage > 0:
        print("  Successfully demonstrated buffer usage!")
    else:
        print("  Buffer was not used - need more aggressive parameters")

    print("\nDemo completed. You can now:")
    print("  - Run your own simulations with different parameters")
    print("  - Test the automatic precision mode")
    print("  - Analyze system behavior under different loads")


def display_welcome_message():
    print("\n" + "=" * 60)
    print("RESTAURANT DELIVERY SMO SIMULATOR")
    print("=" * 60)
    print("\nThis simulator models a restaurant order processing system using:")
    print("  - IEEE Std 610.12-1990 Special Events Method")
    print("  - Mass Service System (SMO) principles")
    print("  - Realistic restaurant delivery business domain")
    print("\nVariant: ИБ И32 П31 Д1031 Д10O3 Д2П2 Д2Б2 OР2 ОД2")
    print("\nKey features:")
    print("  - Step-by-step special events processing")
    print("  - Automatic mode with precision control")
    print("  - Comprehensive statistics and reporting")
    print("  - Formalized scheme visualization (ОД2)")
    print("  - Results with 10% precision and 0.9 confidence")


if __name__ == "__main__":
    display_welcome_message()
    main()
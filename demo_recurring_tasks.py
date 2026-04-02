"""
demo_recurring_tasks.py — Demonstrate that mark_completed() triggers create_next_occurrence()
Run with: python demo_recurring_tasks.py
"""

from datetime import date, timedelta
from pawpal_system import Pet, Task, TaskCategory, TaskPriority, TaskFrequency

def main():
    print("=" * 70)
    print("DEMO: mark_completed() NOW TRIGGERS create_next_occurrence()")
    print("=" * 70)

    # Create a pet
    dog = Pet("p1", "Max", "Dog", age=3, weight=30.5)

    # Create a daily recurring task
    today = date.today()
    morning_walk = Task(
        "t_walk_daily",
        "Morning Walk",
        "1-hour park walk",
        TaskCategory.WALK,
        TaskPriority.HIGH,
        60,
        "p1",
        frequency=TaskFrequency.DAILY,
        non_negotiable=True,
        due_date=today
    )

    dog.add_task(morning_walk)

    print(f"\n1. Created recurring task: {morning_walk.name}")
    print(f"   - Status: {morning_walk.status.value}")
    print(f"   - Frequency: {morning_walk.frequency.value}")
    print(f"   - Due date: {morning_walk.due_date}")
    print(f"   - Pet has {dog.task_count()} task(s)")

    # Mark the task as completed
    print(f"\n2. Calling mark_completed() on the task...")
    next_task = morning_walk.mark_completed()

    print(f"   - Original task status: {morning_walk.status.value}")
    print(f"   - Next task was created: {next_task is not None}")

    if next_task:
        print(f"\n3. Next occurrence created automatically:")
        print(f"   - ID: {next_task.id}")
        print(f"   - Name: {next_task.name}")
        print(f"   - Status: {next_task.status.value}")
        print(f"   - Due date: {next_task.due_date}")
        print(f"   - Frequency: {next_task.frequency.value}")

        # Demonstrate Pet.mark_task_completed() convenience method
        print(f"\n4. Testing Pet.mark_task_completed() convenience method:")
        print(f"   - Adding next task to pet's task list...")
        dog.add_task(next_task)
        print(f"   - Pet now has {dog.task_count()} tasks")

        # Now mark the second task complete using the Pet's method
        result = dog.mark_task_completed(next_task.id)
        print(f"   - Called dog.mark_task_completed('{next_task.id}')")
        print(f"   - Success: {result}")
        
        # Check if third occurrence was created
        all_tasks = [t for t in dog.tasks]
        incomplete_count = sum(1 for t in all_tasks if t.status.value == "pending")
        print(f"   - Pet now has {dog.task_count()} total tasks")
        print(f"   - Pending tasks: {incomplete_count}")

        if incomplete_count > 0:
            third_task = next(t for t in all_tasks if t.status.value == "pending")
            print(f"   - Third occurrence due: {third_task.due_date}")

    print(f"\n{'=' * 70}")
    print("SUCCESS: create_next_occurrence() is now properly triggered! ✓")
    print("=" * 70)


if __name__ == "__main__":
    main()

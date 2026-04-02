"""
main.py — PawPal+ daily schedule demo.
Run with: python main.py
"""

from datetime import date, timedelta
from pawpal_system import (
    Owner, Pet, Task,
    TaskCategory, TaskPriority, TaskFrequency, TaskStatus,
    DayConstraints, EnergyLevel, Scheduler,
)

W = 60
DIV = "-" * W
HDR = "=" * W


def section(title: str) -> None:
    print(f"\n{HDR}\n{title}\n{HDR}")


def main():
    # ── Owner ────────────────────────────────────────────────────────────────
    owner = Owner(name="Sarah", owner_id="owner_001")

    # ── Pets ─────────────────────────────────────────────────────────────────
    dog = Pet("pet_001", "Max", "Dog", age=3, weight=30.5,
              health_notes="Slightly overweight, needs more exercise")

    cat = Pet("pet_002", "Whiskers", "Cat", age=5, weight=4.2,
              health_notes="Sensitive digestion")

    rabbit = Pet("pet_003", "Hoppy", "Rabbit", age=2, weight=1.8,
                 health_notes="Needs daily outdoor time")

    for pet in [dog, cat, rabbit]:
        owner.add_pet(pet)

    # ── Tasks — Dog ──────────────────────────────────────────────────────────
    # Added out of order to demonstrate sorting
    today = date.today()
    dog.add_task(Task("t003", "Play Session",  "Fetch in backyard",
                      TaskCategory.PLAY,         TaskPriority.MEDIUM, 30, dog.id,
                      preferred_time="14:00", due_date=today))

    dog.add_task(Task("t001", "Morning Walk",  "1-hour park walk",
                      TaskCategory.WALK,         TaskPriority.HIGH,   60, dog.id,
                      TaskFrequency.DAILY, non_negotiable=True, preferred_time="08:00", due_date=today))

    # For weekly, set due_date to next Monday
    days_to_monday = ((7 - today.weekday()) % 7) or 7
    weekly_due = today + timedelta(days=days_to_monday)
    dog.add_task(Task("t004", "Grooming",      "Brush fur, check for parasites",
                      TaskCategory.GROOM,        TaskPriority.MEDIUM, 20, dog.id,
                      TaskFrequency.WEEKLY, preferred_time="10:00", due_date=weekly_due))

    dog.add_task(Task("t002", "Breakfast",     "Kibble and fresh water",
                      TaskCategory.FEED,         TaskPriority.HIGH,   15, dog.id,
                      TaskFrequency.DAILY, non_negotiable=True, preferred_time="07:00", due_date=today))

    # ── TIME CONFLICT DEMO: Add overlapping tasks to detect scheduling conflicts ──
    # These tasks intentionally overlap at the same time to test time conflict detection
    dog.add_task(Task("t012", "Training Session", "Teach 'sit' and 'stay'",
                      TaskCategory.PLAY,         TaskPriority.MEDIUM, 25, dog.id,
                      preferred_time="14:00", due_date=today))

    dog.add_task(Task("t013", "Nail Trimming",    "Trim nails, check paws",
                      TaskCategory.GROOM,        TaskPriority.MEDIUM, 20, dog.id,
                      preferred_time="14:15", due_date=today))

    # ── Tasks — Cat ──────────────────────────────────────────────────────────
    # Added out of order
    cat.add_task(Task("t008", "Play Time",     "Laser pointer",
                      TaskCategory.PLAY,         TaskPriority.LOW,    15, cat.id,
                      preferred_time="16:00", due_date=today))

    cat.add_task(Task("t005", "Breakfast",     "Wet food",
                      TaskCategory.FEED,         TaskPriority.HIGH,   10, cat.id,
                      TaskFrequency.DAILY, non_negotiable=True, preferred_time="07:30", due_date=today))

    cat.add_task(Task("t007", "Medication",    "Digestive aid with meal",
                      TaskCategory.MEDICATION,   TaskPriority.HIGH,    5, cat.id,
                      TaskFrequency.DAILY, non_negotiable=True, preferred_time="07:35", due_date=today))

    cat.add_task(Task("t006", "Litter Box",    "Clean and refill",
                      TaskCategory.HEALTH_CHECK, TaskPriority.MEDIUM, 10, cat.id,
                      preferred_time="09:00", due_date=today))

    # ── Tasks — Rabbit ───────────────────────────────────────────────────────
    # Added out of order
    rabbit.add_task(Task("t011", "Health Check","Check for illness or injury",
                         TaskCategory.HEALTH_CHECK, TaskPriority.MEDIUM, 10, rabbit.id,
                         preferred_time="15:00", due_date=today))

    rabbit.add_task(Task("t009", "Breakfast",   "Fresh hay and veg",
                         TaskCategory.FEED,         TaskPriority.HIGH,   15, rabbit.id,
                         TaskFrequency.DAILY, non_negotiable=True, preferred_time="08:00", due_date=today))

    rabbit.add_task(Task("t010", "Outdoor Time","Garden enclosure",
                         TaskCategory.PLAY,         TaskPriority.HIGH,   45, rabbit.id,
                         TaskFrequency.DAILY, non_negotiable=True, preferred_time="10:00", due_date=today))

    # ── Owner summary ────────────────────────────────────────────────────────
    section("OWNER SUMMARY")
    print(f"Owner : {owner.name}  (ID: {owner.owner_id})")
    print(f"Pets  : {owner.pet_count()}")
    print(f"Tasks : {owner.total_task_count()} total")
    for pet in owner.pets:
        note = f"  ⚠  {pet.health_notes}" if pet.health_notes else ""
        print(f"  {pet.name:10} {pet.species:8} {pet.age_label():8} "
              f"{pet.task_count()} tasks{note}")

    # ── High priority ────────────────────────────────────────────────────────
    section("HIGH PRIORITY TASKS")
    for task in owner.get_high_priority_tasks():
        pet = owner.get_pet(task.pet_id)
        marker = " [!]" if task.non_negotiable else ""
        print(f"  {pet.name:10} {task.name:20} "
              f"{task.duration:3} min{marker}")

    # ── Build plan ───────────────────────────────────────────────────────────
    constraints = DayConstraints(
        available_minutes=480,
        energy_level=EnergyLevel.NORMAL,
        special_notes="Standard day — all pets healthy",
    )

    scheduler = Scheduler(owner)

    # ── Demonstrate sorting and filtering ────────────────────────────────────
    section("ALL TASKS SORTED BY TIME")
    all_tasks = owner.get_all_tasks()
    sorted_tasks = scheduler.sort_by_time(all_tasks)
    for task in sorted_tasks:
        pet = owner.get_pet(task.pet_id)
        time_str = f" ({task.preferred_time})" if task.preferred_time else " (anytime)"
        print(f"  {pet.name:10} {task.name:20} {task.status.value:10}{time_str}")

    section("FILTERED: PENDING TASKS ONLY")
    pending_tasks = owner.get_pending_tasks()
    sorted_pending = scheduler.sort_by_time(pending_tasks)
    for task in sorted_pending:
        pet = owner.get_pet(task.pet_id)
        time_str = f" ({task.preferred_time})" if task.preferred_time else " (anytime)"
        print(f"  {pet.name:10} {task.name:20}{time_str}")

    section("FILTERED BY PET NAME: Whiskers")
    whiskers_tasks = owner.get_tasks_by_pet_name("Whiskers")
    for task in whiskers_tasks:
        pref = task.preferred_time if task.preferred_time else "(anytime)"
        print(f"  {task.name:20} {task.status.value:10} {pref}")

    # Mark one task complete and show status-filtered results
    task_to_complete = whiskers_tasks[0] if whiskers_tasks else None
    if task_to_complete:
        scheduler.reschedule_task(task_to_complete.id, TaskStatus.COMPLETED)

    section("FILTERED BY STATUS: COMPLETED")
    completed_tasks = owner.get_tasks_by_status(TaskStatus.COMPLETED)
    for task in completed_tasks:
        print(f"  {task.name:20} {task.pet_id:10} {task.due_date or 'no due date'}")

    plan = scheduler.build_plan(date.today(), constraints)

    # ── Print schedule ───────────────────────────────────────────────────────
    section(f"TODAY'S SCHEDULE — {date.today().strftime('%A, %B %d, %Y')}")
    print(f"Available : {constraints.available_minutes} min "
          f"({'tight day' if constraints.is_tight_day() else 'plenty of time'})")
    print(f"Energy    : {constraints.energy_level.value}")
    if constraints.special_notes:
        print(f"Notes     : {constraints.special_notes}")

    print(f"\n{DIV}")
    for pet in owner.pets:
        pet_tasks = plan.get_tasks_for_pet(pet.id)
        if not pet_tasks:
            continue
        # Sort tasks by preferred time (earliest first), then by priority
        def time_to_minutes(time_str):
            if time_str is None:
                return 12 * 60
            try:
                h, m = map(int, time_str.split(':'))
                return h * 60 + m
            except:
                return 12 * 60
        
        pet_tasks.sort(key=lambda t: (
            time_to_minutes(t.preferred_time),
            0 if t.priority == TaskPriority.HIGH else 1 if t.priority == TaskPriority.MEDIUM else 2,
            t.name
        ))
        subtotal = sum(t.duration for t in pet_tasks)
        print(f"\n  {pet.name} ({pet.species}, {pet.age_label()})")
        for task in pet_tasks:
            marker = " [!]" if task.non_negotiable else "   "
            print(f"  {marker} {task.name:22} "
                  f"{task.priority.value:8} "      # ← .value fixes the enum bug
                  f"{task.duration:3} min")
        print(f"       {'Subtotal':22} {'':8} {subtotal:3} min")

    print(f"\n{DIV}")
    used = plan.total_scheduled_minutes()
    print(f"  Scheduled : {plan.scheduled_count()} tasks  |  {used} min used  |  "
          f"{constraints.available_minutes - used} min remaining")

    if plan.skipped_tasks:
        print(f"\n  Deferred ({plan.skipped_count()} tasks):")
        for task in plan.skipped_tasks:
            pet = owner.get_pet(task.pet_id)
            print(f"    - [{pet.name}] {task.name} ({task.duration} min)")

    if plan.has_conflicts():
        print(f"\n  Conflicts detected:")
        print(plan.conflict_summary())

    print(f"\n{HDR}")
    print("  Done — schedule printed successfully.")
    print(HDR)


if __name__ == "__main__":
    main()
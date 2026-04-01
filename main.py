"""
main.py — PawPal+ daily schedule demo.
Run with: python main.py
"""

from datetime import date
from pawpal_system import (
    Owner, Pet, Task,
    TaskCategory, TaskPriority, TaskFrequency,
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
    dog.add_task(Task("t001", "Morning Walk",  "1-hour park walk",
                      TaskCategory.WALK,         TaskPriority.HIGH,   60, dog.id,
                      TaskFrequency.DAILY, non_negotiable=True, preferred_hour=8))

    dog.add_task(Task("t002", "Breakfast",     "Kibble and fresh water",
                      TaskCategory.FEED,         TaskPriority.HIGH,   15, dog.id,
                      TaskFrequency.DAILY, non_negotiable=True, preferred_hour=7))

    dog.add_task(Task("t003", "Play Session",  "Fetch in backyard",
                      TaskCategory.PLAY,         TaskPriority.MEDIUM, 30, dog.id,
                      preferred_hour=14))

    dog.add_task(Task("t004", "Grooming",      "Brush fur, check for parasites",
                      TaskCategory.GROOM,        TaskPriority.MEDIUM, 20, dog.id,
                      TaskFrequency.WEEKLY, preferred_hour=10))

    # ── Tasks — Cat ──────────────────────────────────────────────────────────
    cat.add_task(Task("t005", "Breakfast",     "Wet food",
                      TaskCategory.FEED,         TaskPriority.HIGH,   10, cat.id,
                      TaskFrequency.DAILY, non_negotiable=True))

    cat.add_task(Task("t006", "Litter Box",    "Clean and refill",
                      TaskCategory.HEALTH_CHECK, TaskPriority.MEDIUM, 10, cat.id))

    cat.add_task(Task("t007", "Medication",    "Digestive aid with meal",
                      TaskCategory.MEDICATION,   TaskPriority.HIGH,    5, cat.id,
                      TaskFrequency.DAILY, non_negotiable=True))

    cat.add_task(Task("t008", "Play Time",     "Laser pointer",
                      TaskCategory.PLAY,         TaskPriority.LOW,    15, cat.id))

    # ── Tasks — Rabbit ───────────────────────────────────────────────────────
    rabbit.add_task(Task("t009", "Breakfast",   "Fresh hay and veg",
                         TaskCategory.FEED,         TaskPriority.HIGH,   15, rabbit.id,
                         TaskFrequency.DAILY, non_negotiable=True))

    rabbit.add_task(Task("t010", "Outdoor Time","Garden enclosure",
                         TaskCategory.PLAY,         TaskPriority.HIGH,   45, rabbit.id,
                         TaskFrequency.DAILY, non_negotiable=True))

    rabbit.add_task(Task("t011", "Health Check","Check for illness or injury",
                         TaskCategory.HEALTH_CHECK, TaskPriority.MEDIUM, 10, rabbit.id))

    # ── Owner summary ────────────────────────────────────────────────────────
    section("OWNER SUMMARY")
    print(f"Owner : {owner.name}  (ID: {owner.owner_id})")
    print(f"Pets  : {owner.pet_count()}")
    print(f"Tasks : {owner.total_task_count()} total")
    for pet in owner.pets:
        note = f"  [!] {pet.health_notes}" if pet.health_notes else ""
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
        blocked_windows=[(120, 180)],  # 2pm-3pm blocked (meeting, etc.)
        energy_level=EnergyLevel.NORMAL,
        special_notes="Standard day — all pets healthy (blocked 2-3pm)",
    )

    scheduler = Scheduler(owner)
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

    # Show conflicts if any detected
    if plan.has_conflicts():
        print(f"\n  [CONFLICTS DETECTED]:")
        for t1, t2 in plan.conflicts:
            pet = owner.get_pet(t1.pet_id)
            print(f"    • {pet.name}: '{t1.name}' + '{t2.name}' may cause issues")

    if plan.skipped_tasks:
        print(f"\n  Deferred ({plan.skipped_count()} tasks):")
        for task in plan.skipped_tasks:
            pet = owner.get_pet(task.pet_id)
            print(f"    - [{pet.name}] {task.name} ({task.duration} min)")

    print(f"\n{HDR}")
    print("  Done — schedule printed successfully.")
    print(HDR)


if __name__ == "__main__":
    main()
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pawpal_system import (
    Owner, Pet, Task,
    TaskCategory, TaskPriority, TaskFrequency, TaskStatus,
    DayConstraints, EnergyLevel, Scheduler,
)


# ── Shared fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def sample_pet():
    return Pet("p1", "Max", "Dog", age=3, weight=12.5)

@pytest.fixture
def sample_task():
    return Task("t1", "Morning Walk", "Walk in the park",
                TaskCategory.WALK, TaskPriority.HIGH, 30, "p1",
                non_negotiable=True)

@pytest.fixture
def owner_with_pets():
    owner = Owner("Sarah", "o1")
    dog = Pet("p1", "Max",     "Dog",    age=3, weight=12.5)
    cat = Pet("p2", "Whiskers","Cat",    age=5, weight=4.2)
    dog.add_task(Task("t1", "Walk",      "Park walk",
                      TaskCategory.WALK, TaskPriority.HIGH,   30, "p1",
                      non_negotiable=True))
    dog.add_task(Task("t2", "Breakfast", "Kibble",
                      TaskCategory.FEED, TaskPriority.HIGH,   15, "p1",
                      non_negotiable=True))
    dog.add_task(Task("t3", "Grooming",  "Brush fur",
                      TaskCategory.GROOM,TaskPriority.LOW,    20, "p1"))
    cat.add_task(Task("t4", "Feed",      "Wet food",
                      TaskCategory.FEED, TaskPriority.HIGH,   10, "p2",
                      non_negotiable=True))
    cat.add_task(Task("t5", "Play",      "Laser pointer",
                      TaskCategory.PLAY, TaskPriority.LOW,    15, "p2"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


# ── Task: mark_complete ───────────────────────────────────────────────────────

def test_mark_completed_changes_status(sample_task):
    """Required test: mark_completed() sets status to COMPLETED."""
    assert sample_task.status == TaskStatus.PENDING
    sample_task.mark_completed()
    assert sample_task.status == TaskStatus.COMPLETED

def test_mark_completed_creates_next_occurrence():
    """mark_completed() should trigger create_next_occurrence() for recurring tasks."""
    from datetime import date
    # Create a daily recurring task
    today = date.today()
    recurring_task = Task(
        "t_daily", "Morning Walk", "Walk in park",
        TaskCategory.WALK, TaskPriority.HIGH, 30, "p1",
        frequency=TaskFrequency.DAILY,
        non_negotiable=True,
        due_date=today
    )
    assert recurring_task.status == TaskStatus.PENDING
    
    # Mark as completed - should return next occurrence
    next_task = recurring_task.mark_completed()
    
    # Verify original task is completed
    assert recurring_task.status == TaskStatus.COMPLETED
    
    # Verify next task was created
    assert next_task is not None
    assert next_task.status == TaskStatus.PENDING
    assert next_task.due_date == (today + __import__('datetime').timedelta(days=1))
    assert next_task.frequency == TaskFrequency.DAILY

def test_mark_completed_returns_none_for_one_time_task():
    """mark_completed() should return None for non-recurring tasks."""
    task = Task("t_once", "One-time bath", "Quick bath",
                TaskCategory.GROOM, TaskPriority.LOW, 20, "p1",
                frequency=TaskFrequency.ONCE)
    next_task = task.mark_completed()
    assert next_task is None
    assert task.status == TaskStatus.COMPLETED

def test_mark_skipped_changes_status(sample_task):
    """mark_skipped() sets status to SKIPPED."""
    sample_task.mark_skipped()
    assert sample_task.status == TaskStatus.SKIPPED

def test_reset_status_returns_to_pending(sample_task):
    """reset_status() brings a completed task back to PENDING."""
    sample_task.mark_completed()
    sample_task.reset_status()
    assert sample_task.status == TaskStatus.PENDING


# ── Task: create_next_occurrence ──────────────────────────────────────────────

def test_create_next_occurrence_daily():
    """Daily task should produce a new task due tomorrow."""
    from datetime import date, timedelta
    today = date.today()
    task = Task("t1", "Walk", "Walk", TaskCategory.WALK, TaskPriority.HIGH,
                30, "p1", frequency=TaskFrequency.DAILY, due_date=today)
    next_task = task.create_next_occurrence()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.status == TaskStatus.PENDING

def test_create_next_occurrence_weekly():
    """Weekly task should produce a new task due in 7 days."""
    from datetime import date, timedelta
    today = date.today()
    task = Task("t1", "Groom", "Brush", TaskCategory.GROOM, TaskPriority.LOW,
                20, "p1", frequency=TaskFrequency.WEEKLY, due_date=today)
    next_task = task.create_next_occurrence()
    assert next_task.due_date == today + timedelta(weeks=1)

def test_create_next_occurrence_once_returns_none():
    """ONCE task should not produce a next occurrence."""
    from datetime import date
    today = date.today()
    task = Task("t1", "Vet", "Vet visit", TaskCategory.HEALTH_CHECK,
                TaskPriority.HIGH, 60, "p1",
                frequency=TaskFrequency.ONCE, due_date=today)
    assert task.create_next_occurrence() is None

def test_create_next_occurrence_no_due_date_returns_none():
    """Task with no due_date set should return None."""
    task = Task("t1", "Walk", "Walk", TaskCategory.WALK, TaskPriority.HIGH,
                30, "p1", frequency=TaskFrequency.DAILY, due_date=None)
    assert task.create_next_occurrence() is None


# ── Task: other methods ───────────────────────────────────────────────────────

def test_is_high_priority_true(sample_task):
    assert sample_task.is_high_priority() is True

def test_is_high_priority_false():
    task = Task("t2", "Bath", "Quick bath",
                TaskCategory.GROOM, TaskPriority.LOW, 20, "p1")
    assert task.is_high_priority() is False

def test_fits_in_exact_minutes(sample_task):
    assert sample_task.fits_in(30) is True

def test_fits_in_more_than_enough(sample_task):
    assert sample_task.fits_in(60) is True

def test_fits_in_not_enough(sample_task):
    assert sample_task.fits_in(29) is False

def test_summary_uses_enum_value(sample_task):
    """summary() should show 'high' not 'TaskPriority.HIGH'."""
    result = sample_task.summary()
    assert "TaskPriority" not in result
    assert "high" in result


# ── Pet: task addition ────────────────────────────────────────────────────────

def test_add_task_increases_count(sample_pet, sample_task):
    """Required test: adding a task increases pet's task count by 1."""
    before = sample_pet.task_count()
    sample_pet.add_task(sample_task)
    assert sample_pet.task_count() == before + 1

def test_add_task_sets_pet_id(sample_pet, sample_task):
    """add_task() should assign the pet's id to the task."""
    sample_pet.add_task(sample_task)
    assert sample_task.pet_id == sample_pet.id

def test_get_pending_tasks_excludes_completed(sample_pet):
    t1 = Task("t1", "Walk", "Walk", TaskCategory.WALK, TaskPriority.HIGH, 30, "p1")
    t2 = Task("t2", "Feed", "Feed", TaskCategory.FEED, TaskPriority.HIGH, 10, "p1")
    t2.mark_completed()
    sample_pet.add_task(t1)
    sample_pet.add_task(t2)
    pending = sample_pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].id == "t1"


# ── Owner ─────────────────────────────────────────────────────────────────────

def test_owner_add_pet_increases_count():
    owner = Owner("Sarah", "o1")
    owner.add_pet(Pet("p1", "Max", "Dog", 3, 12.5))
    assert owner.pet_count() == 1

def test_owner_remove_pet(owner_with_pets):
    result = owner_with_pets.remove_pet("p1")
    assert result is True
    assert owner_with_pets.pet_count() == 1

def test_owner_remove_nonexistent_pet(owner_with_pets):
    result = owner_with_pets.remove_pet("p999")
    assert result is False

def test_owner_get_all_tasks_count(owner_with_pets):
    """All tasks across all pets should be returned."""
    assert owner_with_pets.total_task_count() == 5

def test_owner_get_high_priority_tasks(owner_with_pets):
    high = owner_with_pets.get_high_priority_tasks()
    assert all(t.priority == TaskPriority.HIGH for t in high)


# ── Scheduler ─────────────────────────────────────────────────────────────────

def test_scheduler_plan_is_valid(owner_with_pets):
    """Plan total minutes must not exceed available minutes."""
    constraints = DayConstraints(available_minutes=120)
    plan = Scheduler(owner_with_pets).build_plan(__import__('datetime').date.today(), constraints)
    assert plan.is_valid()

def test_scheduler_non_negotiable_scheduled_first(owner_with_pets):
    """Non-negotiable tasks should always appear in scheduled, not skipped."""
    constraints = DayConstraints(available_minutes=60)
    plan = Scheduler(owner_with_pets).build_plan(__import__('datetime').date.today(), constraints)
    skipped_ids = {t.id for t in plan.skipped_tasks}
    for task in owner_with_pets.get_all_tasks():
        if task.non_negotiable:
            assert task.id not in skipped_ids, f"{task.name} was skipped but is non-negotiable"

def test_scheduler_skips_tasks_that_dont_fit(owner_with_pets):
    """With very little time, low-priority tasks should be skipped."""
    constraints = DayConstraints(available_minutes=30)
    plan = Scheduler(owner_with_pets).build_plan(__import__('datetime').date.today(), constraints)
    assert plan.skipped_count() > 0

def test_scheduler_tight_day_flag():
    constraints = DayConstraints(available_minutes=60)
    assert constraints.is_tight_day() is True

def test_scheduler_not_tight_day():
    constraints = DayConstraints(available_minutes=480)
    assert constraints.is_tight_day() is False


# ── Sorting and filtering tests ───────────────────────────────────────────────

def test_sort_by_time_orders_correctly(owner_with_pets):
    """Tasks with earlier preferred_time should come first."""
    scheduler = Scheduler(owner_with_pets)
    tasks = [
        Task("t1", "Late task",  "desc", TaskCategory.PLAY, TaskPriority.LOW,
             10, "p1", preferred_time="14:00"),
        Task("t2", "Early task", "desc", TaskCategory.FEED, TaskPriority.HIGH,
             10, "p1", preferred_time="07:00"),
        Task("t3", "No time",    "desc", TaskCategory.GROOM, TaskPriority.LOW,
             10, "p1", preferred_time=None),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    assert sorted_tasks[0].name == "Early task"  # 07:00 comes first
    assert sorted_tasks[1].name == "No time"     # None defaults to 12:00 (noon)
    assert sorted_tasks[2].name == "Late task"   # 14:00 comes last

def test_filter_by_status(owner_with_pets):
    """get_tasks_by_status should return only tasks with matching status."""
    all_tasks = owner_with_pets.get_all_tasks()
    all_tasks[0].mark_completed()
    completed = owner_with_pets.get_tasks_by_status(TaskStatus.COMPLETED)
    assert len(completed) == 1
    assert all(t.status == TaskStatus.COMPLETED for t in completed)

def test_filter_by_pet_name(owner_with_pets):
    """get_tasks_by_pet_name should return only that pet's tasks."""
    tasks = owner_with_pets.get_tasks_by_pet_name("Whiskers")
    assert len(tasks) == 2
    assert all(t.pet_id == "p2" for t in tasks)


def test_scheduler_detects_time_conflict_for_duplicate_times():
    """Scheduler should detect a time conflict when two tasks occupy the same time window."""
    owner = Owner("Dana", "o1")
    pet = Pet("p1", "Buddy", "Dog", age=4, weight=25.0)
    t1 = Task("t1", "Morning Walk", "Walk in park", TaskCategory.WALK,
              TaskPriority.HIGH, 30, "p1", preferred_time="08:00")
    t2 = Task("t2", "Play", "Fetch ball", TaskCategory.PLAY,
              TaskPriority.MEDIUM, 15, "p1", preferred_time="08:00")
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)

    constraints = DayConstraints(available_minutes=120)
    plan = Scheduler(owner).build_plan(__import__('datetime').date.today(), constraints)

    assert plan.time_conflicts, "Expected a time conflict for duplicate task times"
    assert any((c[0].id == "t1" and c[1].id == "t2") or (c[0].id == "t2" and c[1].id == "t1")
               for c in plan.time_conflicts)

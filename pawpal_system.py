from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional, Tuple
from enum import Enum


class TaskFrequency(Enum):
    """Frequency of task recurrence."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskStatus(Enum):
    """Completion status of a task."""
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Priority level for a task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCategory(Enum):
    """Category of care task."""
    WALK = "walk"
    FEED = "feed"
    GROOM = "groom"
    MEDICATION = "med"
    PLAY = "play"
    HEALTH_CHECK = "health_check"


class EnergyLevel(Enum):
    """Pet's energy level for the day."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class Pet:
    """Represents a pet that needs care."""
    id: str
    name: str
    species: str
    age: int
    weight: float
    health_notes: Optional[str] = None
    tasks: list[Task] = field(default_factory=list)

    def age_label(self) -> str:
        """Return a human-readable age description."""
        if self.age < 1:
            return "Kitten/Puppy"
        elif self.age < 3:
            return "Young"
        elif self.age < 7:
            return "Adult"
        else:
            return "Senior"

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        task.pet_id = self.id
        self.tasks.append(task)

    def mark_task_completed(self, task_id: str) -> bool:
        """Mark a task as completed by ID. If recurring, automatically adds the next occurrence.
        
        Returns:
            True if task was found and marked completed, False otherwise.
        """
        for task in self.tasks:
            if task.id == task_id:
                next_task = task.mark_completed()
                # Add the next occurrence if it was created
                if next_task:
                    self.add_task(next_task)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return all pending tasks for this pet."""
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]

    def get_high_priority_tasks(self) -> list[Task]:
        """Return all high-priority tasks for this pet."""
        return [t for t in self.tasks if t.is_high_priority()]

    def task_count(self) -> int:
        """Return total number of tasks for this pet."""
        return len(self.tasks)


@dataclass
class Task:
    """Represents a care task for a specific pet."""
    id: str
    name: str
    description: str
    category: TaskCategory
    priority: TaskPriority
    duration: int  # minutes
    pet_id: str
    frequency: TaskFrequency = TaskFrequency.DAILY
    non_negotiable: bool = False
    status: TaskStatus = TaskStatus.PENDING
    preferred_time: Optional[str] = None  # "HH:MM" format (e.g., "08:00" for 8am), or None for anytime
    due_date: Optional[date] = None  # Date when the task is due

    def is_high_priority(self) -> bool:
        """Return True if priority is 'high'."""
        return self.priority == TaskPriority.HIGH

    def fits_in(self, minutes: int) -> bool:
        """Return True if task duration <= available minutes."""
        return self.duration <= minutes

    def summary(self) -> str:
        """Return a formatted summary of the task."""
        status_str = f"[{self.status.value}]" if self.status != TaskStatus.PENDING else ""
        return f"{self.name} ({self.duration}min, {self.priority.value}) {status_str}".strip()

    def mark_completed(self) -> Optional['Task']:
        """Mark task as completed. If recurring, create and return the next occurrence.
        
        Returns:
            The next task occurrence if this task is recurring, None otherwise.
        """
        self.status = TaskStatus.COMPLETED
        # Automatically create the next occurrence for recurring tasks
        if self.frequency != TaskFrequency.ONCE:
            return self.create_next_occurrence()
        return None

    def mark_skipped(self) -> None:
        """Mark task as skipped."""
        self.status = TaskStatus.SKIPPED

    def reset_status(self) -> None:
        """Reset task status to pending."""
        self.status = TaskStatus.PENDING

    def create_next_occurrence(self) -> Optional['Task']:
        """Create the next occurrence of a recurring task."""
        if self.frequency == TaskFrequency.ONCE:
            return None
        if self.due_date is None:
            return None
        
        next_due_date = None
        if self.frequency == TaskFrequency.DAILY:
            next_due_date = self.due_date + timedelta(days=1)
        elif self.frequency == TaskFrequency.WEEKLY:
            next_due_date = self.due_date + timedelta(weeks=1)
        elif self.frequency == TaskFrequency.MONTHLY:
            # Approximate monthly as 30 days
            next_due_date = self.due_date + timedelta(days=30)
        
        if next_due_date:
            # Create new task with new ID, reset status, new due_date
            new_id = f"{self.id}_next_{next_due_date.isoformat()}"
            return Task(
                id=new_id,
                name=self.name,
                description=self.description,
                category=self.category,
                priority=self.priority,
                duration=self.duration,
                pet_id=self.pet_id,
                frequency=self.frequency,
                non_negotiable=self.non_negotiable,
                status=TaskStatus.PENDING,
                preferred_time=self.preferred_time,
                due_date=next_due_date
            )
        return None


class DayConstraints:
    """Represents constraints and context for a specific day's planning."""

    def __init__(
        self,
        available_minutes: int,
        blocked_windows: Optional[list[Tuple[int, int]]] = None,
        energy_level: EnergyLevel = EnergyLevel.NORMAL,
        special_notes: Optional[str] = None,
    ):
        """Initialize day constraints with available time, blocked windows, energy level, and notes."""
        self.available_minutes = available_minutes
        self.blocked_windows = blocked_windows or []
        self.energy_level = energy_level
        self.special_notes = special_notes

    def is_tight_day(self) -> bool:
        """Return True if available time is very limited (< 180 minutes)."""
        return self.available_minutes < 180

    def to_prompt_str(self) -> str:
        """Format constraints as a string for AI/scheduler input."""
        prompt = f"Available time: {self.available_minutes} minutes\n"
        prompt += f"Pet energy level: {self.energy_level.value}\n"
        if self.blocked_windows:
            blocked_str = ", ".join(
                [f"{start}-{end}" for start, end in self.blocked_windows]
            )
            prompt += f"Blocked time windows (in minutes): {blocked_str}\n"
        if self.special_notes:
            prompt += f"Special notes: {self.special_notes}\n"
        return prompt


class DailyPlan:
    """Represents a complete schedule for one day across all pets."""

    def __init__(
        self,
        date: date,
        pets: list[Pet],
        constraints: DayConstraints,
        scheduled_tasks: list[Task] = None,
        skipped_tasks: list[Task] = None,
    ):
        """Initialize a daily plan for the given date, pets, and constraints."""
        self.date = date
        self.pets = pets
        self.constraints = constraints
        self.scheduled_tasks = scheduled_tasks or []
        self.skipped_tasks = skipped_tasks or []
        self.conflicts: list[tuple[Task, Task]] = []  # Behavioral conflicts (same pet, incompatible categories)
        self.time_conflicts: list[tuple[Task, Task]] = []  # Time-based conflicts (overlapping scheduled times)

    def skipped_count(self) -> int:
        """Return the number of skipped tasks."""
        return len(self.skipped_tasks)

    def scheduled_count(self) -> int:
        """Return the number of scheduled tasks."""
        return len(self.scheduled_tasks)

    def total_scheduled_minutes(self) -> int:
        """Return total duration of all scheduled tasks."""
        return sum(task.duration for task in self.scheduled_tasks)

    def is_valid(self) -> bool:
        """Return True if scheduled tasks fit within constraints."""
        return self.total_scheduled_minutes() <= self.constraints.available_minutes

    def add_task(self, task: Task, skip: bool = False) -> None:
        """Add a task to the plan (scheduled or skipped)."""
        if skip:
            self.skipped_tasks.append(task)
        else:
            self.scheduled_tasks.append(task)

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Return all tasks scheduled for a specific pet."""
        return [t for t in self.scheduled_tasks if t.pet_id == pet_id]

    def has_conflicts(self) -> bool:
        """Return True if any task conflicts were detected (behavioral or time-based)."""
        return len(self.conflicts) > 0 or len(self.time_conflicts) > 0

    def conflict_summary(self) -> str:
        """Return a human-readable summary of all conflicts (behavioral and time-based)."""
        if not self.conflicts and not self.time_conflicts:
            return "No conflicts detected."
        
        lines = []
        
        if self.conflicts:
            lines.append(f"⚠ {len(self.conflicts)} behavioral conflict(s) detected:")
            for t1, t2 in self.conflicts:
                pet = next((p for p in self.pets if p.id == t1.pet_id), None)
                pet_name = pet.name if pet else "Unknown"
                lines.append(f"  • [{pet_name}] {t1.name} + {t2.name} (incompatible categories)")
        
        if self.time_conflicts:
            if lines:
                lines.append("")  # Blank line separator
            lines.append(f"⚠ {len(self.time_conflicts)} time-based conflict(s) detected:")
            for t1, t2 in self.time_conflicts:
                pet1 = next((p for p in self.pets if p.id == t1.pet_id), None)
                pet2 = next((p for p in self.pets if p.id == t2.pet_id), None)
                pet1_name = pet1.name if pet1 else "Unknown"
                pet2_name = pet2.name if pet2 else "Unknown"
                time_overlap = f"{t1.preferred_time} duration {t1.duration}min overlaps {t2.preferred_time} duration {t2.duration}min"
                lines.append(f"  • [{pet1_name}] {t1.name} ↔ [{pet2_name}] {t2.name}")
                lines.append(f"      {time_overlap}")
        
        return "\n".join(lines)


class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str, owner_id: str):
        """Initialize an owner."""
        self.name = name
        self.owner_id = owner_id
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by ID. Return True if successful."""
        for i, pet in enumerate(self.pets):
            if pet.id == pet_id:
                self.pets.pop(i)
                return True
        return False

    def get_pet(self, pet_id: str) -> Optional[Pet]:
        """Retrieve a specific pet by ID."""
        for pet in self.pets:
            if pet.id == pet_id:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return a flattened list of all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return all pending tasks across all pets."""
        return [t for t in self.get_all_tasks() if t.status == TaskStatus.PENDING]

    def get_high_priority_tasks(self) -> list[Task]:
        """Return all high-priority tasks across all pets."""
        return [t for t in self.get_all_tasks() if t.is_high_priority()]

    def pet_count(self) -> int:
        """Return the number of pets."""
        return len(self.pets)

    def total_task_count(self) -> int:
        """Return total number of tasks across all pets."""
        return len(self.get_all_tasks())

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        """Return tasks across all pets matching the given status."""
        return [t for t in self.get_all_tasks() if t.status == status]

    def get_tasks_by_pet_name(self, pet_name: str) -> list[Task]:
        """Return all tasks for pet(s) with matching name (case-insensitive)."""
        filtered_tasks = []
        pet_name_lower = pet_name.strip().lower()
        for pet in self.pets:
            if pet.name.lower() == pet_name_lower:
                filtered_tasks.extend(pet.tasks)
        return filtered_tasks


class Scheduler:
    """Retrieves, prioritizes, and schedules tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Initialize scheduler with an owner."""
        self.owner = owner

    def _time_to_minutes(self, time_str: Optional[str]) -> int:
        """Convert "HH:MM" string to minutes past midnight. Return 12*60=720 (noon) if None."""
        if time_str is None:
            return 12 * 60  # Default to noon
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except ValueError:
            return 12 * 60  # Default on parse error

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by their preferred_time in "HH:MM" format using a lambda key."""
        return sorted(tasks, key=lambda t: self._time_to_minutes(t.preferred_time))

    def get_available_tasks(self) -> list[Task]:
        """Return all pending tasks from the owner's pets."""
        return self.owner.get_pending_tasks()

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by non-negotiable flag then priority (high > medium > low), then by time preference."""
        priority_order = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}
        return sorted(
            tasks,
            key=lambda t: (
                not t.non_negotiable,  # False (non-negotiable) comes first
                priority_order.get(t.priority, 3),
                self._time_to_minutes(t.preferred_time),  # Use time in minutes
                t.name,
            ),
        )

    def should_run_today(self, task: Task, plan_date: date) -> bool:
        """Check if recurring task should be scheduled for the given date."""
        if task.due_date is None:
            # Fallback to old logic if no due_date
            if task.frequency == TaskFrequency.ONCE:
                return task.status == TaskStatus.PENDING
            elif task.frequency == TaskFrequency.DAILY:
                return True
            elif task.frequency == TaskFrequency.WEEKLY:
                return plan_date.weekday() == 0  # Monday
            elif task.frequency == TaskFrequency.MONTHLY:
                return plan_date.day == 1
            return False
        else:
            # New logic: run if due_date matches plan_date and status is pending
            return task.due_date == plan_date and task.status == TaskStatus.PENDING

    def detect_conflicts(self, plan: DailyPlan) -> list[tuple[Task, Task]]:
        """Return list of task pairs that conflict (incompatible for same pet)."""
        conflicts = []
        scheduled = plan.scheduled_tasks
        for i, t1 in enumerate(scheduled):
            for t2 in scheduled[i + 1:]:
                if t1.pet_id == t2.pet_id:
                    if self._are_incompatible(t1, t2) or self._are_play_feed_incompatible(t1, t2):
                        conflicts.append((t1, t2))
        return conflicts

    def _are_incompatible(self, t1: Task, t2: Task) -> bool:
        """Check if two tasks for same pet shouldn't happen sequentially."""
        # Two walks back-to-back exhaust the pet without rest
        if t1.category == TaskCategory.WALK and t2.category == TaskCategory.WALK:
            return True
        return False

    def _are_play_feed_incompatible(self, t1: Task, t2: Task) -> bool:
        """Calculate whether play and feed tasks are in conflict by time gap.

        For the same pet, PLAY and FEED tasks are allowed only if they are at least
        15 minutes apart. This method uses preferred_time (HH:MM) to compute a
        minute-based gap. If either task has no preferred_time, it defaults to noon
        via _time_to_minutes() and then compares.

        Returns:
            True if tasks are PLAY/FEED and gap < 15 minutes (incompatible),
            False otherwise.
        """
        if not ((t1.category == TaskCategory.PLAY and t2.category == TaskCategory.FEED) or \
               (t1.category == TaskCategory.FEED and t2.category == TaskCategory.PLAY)):
            return False
        # Calculate time gap
        t1_min = self._time_to_minutes(t1.preferred_time)
        t2_min = self._time_to_minutes(t2.preferred_time)
        gap = abs(t1_min - t2_min)
        return gap < 15  # Incompatible if gap < 15 minutes

    def _tasks_have_time_conflict(self, task1: Task, task2: Task) -> bool:
        """Check if two tasks have overlapping time windows.
        
        Returns True if task1's scheduled time overlaps with task2's scheduled time,
        considering task duration (e.g., 08:00 for 30min conflicts with 08:15 for 30min).
        Returns False if either task lacks a preferred_time.
        """
        # Must have times to conflict
        if not task1.preferred_time or not task2.preferred_time:
            return False
        
        # Convert to minutes past midnight
        t1_start = self._time_to_minutes(task1.preferred_time)
        t2_start = self._time_to_minutes(task2.preferred_time)
        
        # Calculate end times
        t1_end = t1_start + task1.duration
        t2_end = t2_start + task2.duration
        
        # Check for overlap: two intervals [a,b) and [c,d) overlap if max(a,c) < min(b,d)
        return max(t1_start, t2_start) < min(t1_end, t2_end)

    def detect_time_conflicts(self, plan: DailyPlan) -> list[tuple[Task, Task]]:
        """Return list of task pairs with overlapping time windows in the daily plan.
        
        This detects scheduling conflicts where two tasks (for same or different pets)
        are scheduled to run at overlapping times. Works across all pets—not limited
        to same-pet conflicts.
        
        Returns:
            list of (task1, task2) tuples with overlapping time windows.
        """
        conflicts = []
        for i, t1 in enumerate(plan.scheduled_tasks):
            for t2 in plan.scheduled_tasks[i + 1:]:
                if self._tasks_have_time_conflict(t1, t2):
                    conflicts.append((t1, t2))
        return conflicts

    def build_plan(
        self, date_for_plan: date, constraints: DayConstraints
    ) -> DailyPlan:
        """Build a priority-ordered daily plan, scheduling tasks that fit and skipping the rest.

        Accounts for:
        - Recurring task frequency (only schedule if should run today)
        - Blocked time windows
        - Task priority and time preferences
        - Task duration constraints
        """
        available_tasks = self.get_available_tasks()

        # Filter out tasks that shouldn't run today
        tasks_for_today = [t for t in available_tasks if self.should_run_today(t, date_for_plan)]
        prioritized_tasks = self.prioritize_tasks(tasks_for_today)

        plan = DailyPlan(
            date=date_for_plan,
            pets=self.owner.pets,
            constraints=constraints,
        )

        # Calculate available minutes accounting for blocked windows
        remaining_minutes = constraints.available_minutes
        if constraints.blocked_windows:
            blocked_duration = sum(end - start for start, end in constraints.blocked_windows)
            remaining_minutes -= blocked_duration

        # Schedule tasks greedily
        for task in prioritized_tasks:
            if task.fits_in(remaining_minutes):
                plan.add_task(task, skip=False)
                remaining_minutes -= task.duration
            else:
                plan.add_task(task, skip=True)

        # Detect and log conflicts (lightweight warnings, non-fatal)
        behavioral_conflicts = self.detect_conflicts(plan)
        plan.conflicts = behavioral_conflicts  # Behavioral conflicts (incompatible categories)
        
        time_conflicts = self.detect_time_conflicts(plan)
        plan.time_conflicts = time_conflicts  # Time-based conflicts (overlapping schedules)

        return plan

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        """Get all tasks for a specific pet."""
        pet = self.owner.get_pet(pet_id)
        if pet:
            return pet.get_pending_tasks()
        return []

    def reschedule_task(self, task_id: str, new_status: TaskStatus) -> bool:
        """Update a task's status and handle recurring task logic.

        This method updates the status of a task identified by task_id to the specified
        new_status. For COMPLETED tasks, it automatically creates and adds the next
        occurrence for recurring tasks (daily, weekly, monthly).

        Args:
            task_id: The unique identifier of the task to update
            new_status: The new status to assign (PENDING, COMPLETED, or SKIPPED)

        Returns:
            True if the task was found and updated successfully, False otherwise

        Note:
            When marking a task as COMPLETED, if it's a recurring task, the next
            occurrence is automatically created and added to the appropriate pet's
            task list with the correct due date.
        """
        for task in self.owner.get_all_tasks():
            if task.id == task_id:
                # Use mark_completed() to properly handle recurring tasks
                if new_status == TaskStatus.COMPLETED:
                    next_task = task.mark_completed()
                    if next_task:
                        pet = self.owner.get_pet(task.pet_id)
                        if pet:
                            pet.add_task(next_task)
                else:
                    # For other statuses, set directly
                    if new_status == TaskStatus.SKIPPED:
                        task.mark_skipped()
                    elif new_status == TaskStatus.PENDING:
                        task.reset_status()
                    else:
                        task.status = new_status
                return True
        return False


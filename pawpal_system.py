from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
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

    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED

    def mark_skipped(self) -> None:
        """Mark task as skipped."""
        self.status = TaskStatus.SKIPPED

    def reset_status(self) -> None:
        """Reset task status to pending."""
        self.status = TaskStatus.PENDING


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
        """Return True if available time is very limited (< 120 minutes)."""
        return self.available_minutes < 120

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


class Scheduler:
    """Retrieves, prioritizes, and schedules tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Initialize scheduler with an owner."""
        self.owner = owner

    def get_available_tasks(self) -> list[Task]:
        """Return all pending tasks from the owner's pets."""
        return self.owner.get_pending_tasks()

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by non-negotiable flag then priority (high > medium > low)."""
        priority_order = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}
        return sorted(
            tasks,
            key=lambda t: (
                not t.non_negotiable,  # False (non-negotiable) comes first
                priority_order.get(t.priority, 3),
                t.name,
            ),
        )

    def build_plan(
        self, date_for_plan: date, constraints: DayConstraints
    ) -> DailyPlan:
        """Build a priority-ordered daily plan, scheduling tasks that fit and skipping the rest."""
        available_tasks = self.get_available_tasks()
        prioritized_tasks = self.prioritize_tasks(available_tasks)

        plan = DailyPlan(
            date=date_for_plan,
            pets=self.owner.pets,
            constraints=constraints,
        )

        remaining_minutes = constraints.available_minutes

        for task in prioritized_tasks:
            if task.fits_in(remaining_minutes):
                plan.add_task(task, skip=False)
                remaining_minutes -= task.duration
            else:
                plan.add_task(task, skip=True)

        return plan

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        """Get all tasks for a specific pet."""
        pet = self.owner.get_pet(pet_id)
        if pet:
            return pet.get_pending_tasks()
        return []

    def reschedule_task(self, task_id: str, new_status: TaskStatus) -> bool:
        """Update a task's status. Return True if successful."""
        for task in self.owner.get_all_tasks():
            if task.id == task_id:
                task.status = new_status
                return True
        return False


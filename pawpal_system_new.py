from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Pet:
    """Represents a pet that needs care."""
    id: str
    name: str
    species: str
    age: int
    weight: float
    health_notes: Optional[str] = None

    def age_label(self) -> str:
        """Return a human-readable age description."""
        pass

    def has_health_notes(self) -> bool:
        """Check if health notes exist."""
        pass


@dataclass
class Task:
    """Represents a care task for a specific pet."""
    id: str
    name: str
    category: str
    priority: str  # 'low', 'medium', 'high'
    duration: int  # minutes
    pet_id: str
    non_negotiable: bool = False

    def is_high_priority(self) -> bool:
        """Return True if priority is 'high'."""
        pass

    def fits_in(self, minutes: int) -> bool:
        """Return True if task duration <= available minutes."""
        pass

    def summary(self) -> str:
        """Return a formatted summary of the task."""
        pass


class DayConstraints:
    """Represents constraints and context for a specific day's planning."""

    def __init__(
        self,
        available_minutes: int,
        blocked_windows: list = None,
        energy_level: str = "normal",
        special_notes: Optional[str] = None,
    ):
        self.available_minutes = available_minutes
        self.blocked_windows = blocked_windows or []
        self.energy_level = energy_level  # 'low', 'normal', 'high'
        self.special_notes = special_notes

    def is_tight_day(self) -> bool:
        """Return True if available time is very limited."""
        pass

    def to_prompt_str(self) -> str:
        """Format constraints as a string for AI/scheduler input."""
        pass


class DailyPlan:
    """Represents a complete schedule for one day across all pets."""

    def __init__(
        self,
        date: date,
        pets: list[Pet],
        scheduled_tasks: list[Task] = None,
        skipped_tasks: list[Task] = None,
    ):
        self.date = date
        self.pets = pets
        self.scheduled_tasks = scheduled_tasks or []
        self.skipped_tasks = skipped_tasks or []

    def skipped_count(self) -> int:
        """Return the number of skipped tasks."""
        pass

    def scheduled_count(self) -> int:
        """Return the number of scheduled tasks."""
        pass

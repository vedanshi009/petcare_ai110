# PawPal+ Class Diagram

```mermaid
classDiagram
    class Owner {
        -name: str
        -owner_id: str
        -pets: Pet[]
        +add_pet(pet: Pet) void
        +remove_pet(pet_id: str) bool
        +get_pet(pet_id: str) Optional~Pet~
        +get_all_tasks() Task[]
        +get_pending_tasks() Task[]
        +get_high_priority_tasks() Task[]
        +pet_count() int
        +total_task_count() int
        +get_tasks_by_status(status: TaskStatus) Task[]
        +get_tasks_by_pet_name(pet_name: str) Task[]
    }

    class Pet {
        -id: str
        -name: str
        -species: str
        -age: int
        -weight: float
        -health_notes: Optional~str~
        -tasks: Task[]
        +age_label() str
        +add_task(task: Task) void
        +mark_task_completed(task_id: str) bool
        +get_pending_tasks() Task[]
        +get_high_priority_tasks() Task[]
        +task_count() int
    }

    class Task {
        -id: str
        -name: str
        -description: str
        -category: TaskCategory
        -priority: TaskPriority
        -duration: int
        -pet_id: str
        -frequency: TaskFrequency
        -non_negotiable: bool
        -status: TaskStatus
        -preferred_time: Optional~str~
        -due_date: Optional~date~
        +is_high_priority() bool
        +fits_in(minutes: int) bool
        +summary() str
        +mark_completed() Optional~Task~
        +mark_skipped() void
        +reset_status() void
        +create_next_occurrence() Optional~Task~
    }

    class DayConstraints {
        -available_minutes: int
        -blocked_windows: list~Tuple~
        -energy_level: EnergyLevel
        -special_notes: Optional~str~
        +is_tight_day() bool
        +to_prompt_str() str
    }

    class DailyPlan {
        -date: date
        -pets: Pet[]
        -constraints: DayConstraints
        -scheduled_tasks: Task[]
        -skipped_tasks: Task[]
        -conflicts: Tuple~Task, Task~[]
        -time_conflicts: Tuple~Task, Task~[]
        +skipped_count() int
        +scheduled_count() int
        +total_scheduled_minutes() int
        +is_valid() bool
        +add_task(task: Task, skip: bool) void
        +get_tasks_for_pet(pet_id: str) Task[]
        +has_conflicts() bool
        +conflict_summary() str
    }

    class Scheduler {
        -owner: Owner
        +get_available_tasks() Task[]
        +prioritize_tasks(tasks: Task[]) Task[]
        +sort_by_time(tasks: Task[]) Task[]
        +should_run_today(task: Task, plan_date: date) bool
        +detect_conflicts(plan: DailyPlan) Tuple~Task, Task~[]
        +detect_time_conflicts(plan: DailyPlan) Tuple~Task, Task~[]
        +build_plan(date_for_plan: date, constraints: DayConstraints) DailyPlan
        +get_tasks_by_pet(pet_id: str) Task[]
        +reschedule_task(task_id: str, new_status: TaskStatus) bool
    }

    class TaskFrequency {
        <<enumeration>>
        ONCE
        DAILY
        WEEKLY
        MONTHLY
    }

    class TaskStatus {
        <<enumeration>>
        PENDING
        COMPLETED
        SKIPPED
    }

    class TaskPriority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
    }

    class TaskCategory {
        <<enumeration>>
        WALK
        FEED
        GROOM
        MEDICATION
        PLAY
        HEALTH_CHECK
    }

    class EnergyLevel {
        <<enumeration>>
        LOW
        NORMAL
        HIGH
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "*" Task : has
    Task --> TaskFrequency : frequency
    Task --> TaskStatus : status
    Task --> TaskPriority : priority
    Task --> TaskCategory : category
    Scheduler "1" --> "1" Owner : schedules_for
    Scheduler --> DailyPlan : creates
    DailyPlan "1" --> "1" DayConstraints : created_with
    DailyPlan "1" --> "*" Task : schedules/skips
    DailyPlan "1" --> "*" Pet : plans_for
    DayConstraints --> EnergyLevel : has
```

## Class Descriptions

### Owner
Manages multiple pets and provides access to all their tasks.
- **Attributes:** name, owner_id, pets (list of Pet objects)
- **Methods:** 
  - `add_pet()`: Add a pet to the owner's collection
  - `remove_pet()`: Remove a pet by ID
  - `get_pet()`: Retrieve a specific pet by ID
  - `get_all_tasks()`: Flattened list of all tasks across all pets
  - `get_pending_tasks()`: All pending tasks across all pets
  - `get_high_priority_tasks()`: All high-priority tasks across all pets
  - `get_tasks_by_status()`: Tasks matching a given status
  - `get_tasks_by_pet_name()`: All tasks for a named pet

### Pet
Represents a pet that needs care.
- **Attributes:** id, name, species, age (in years), weight, health_notes (optional), tasks (list of Task objects)
- **Methods:** 
  - `age_label()`: Returns a human-readable age description (Kitten/Puppy, Young, Adult, Senior)
  - `add_task()`: Add a task to this pet
  - `mark_task_completed()`: Mark a task as completed by ID; automatically creates next occurrence if recurring
  - `get_pending_tasks()`: Return all pending tasks for this pet
  - `get_high_priority_tasks()`: Return all high-priority tasks for this pet
  - `task_count()`: Return total number of tasks for this pet

### Task
Represents a care task for a specific pet.
- **Attributes:** id, name, description, category (TaskCategory enum), priority (TaskPriority enum), duration (minutes), pet_id, frequency (TaskFrequency enum), non_negotiable, status (TaskStatus enum), preferred_time (optional HH:MM format), due_date (optional)
- **Methods:**
  - `is_high_priority()`: Returns true if priority is HIGH
  - `fits_in(minutes)`: Returns true if task duration ≤ available minutes
  - `summary()`: Returns a formatted summary of the task
  - `mark_completed()`: Mark task as completed; creates and returns next occurrence if recurring
  - `mark_skipped()`: Mark task as skipped
  - `reset_status()`: Reset task status to pending
  - `create_next_occurrence()`: Create the next occurrence of a recurring task

### Scheduler
Retrieves, prioritizes, and schedules tasks across all of an owner's pets.
- **Attributes:** owner (Owner object)
- **Methods:**
  - `get_available_tasks()`: Return all pending tasks from the owner's pets
  - `prioritize_tasks()`: Sort tasks by non-negotiable flag, priority, and time preference
  - `sort_by_time()`: Sort tasks by preferred_time
  - `should_run_today()`: Check if recurring task should be scheduled for a given date
  - `detect_conflicts()`: Return task pairs with behavioral conflicts (same pet, incompatible categories)
  - `detect_time_conflicts()`: Return task pairs with overlapping time windows
  - `build_plan()`: Build a priority-ordered daily plan, scheduling tasks that fit
  - `get_tasks_by_pet()`: Get all pending tasks for a specific pet
  - `reschedule_task()`: Update a task's status and handle recurring task logic

### DayConstraints
Represents constraints and context for a specific day's planning.
- **Attributes:** available_minutes, blocked_windows (list of time windows), energy_level (EnergyLevel enum), special_notes (optional)
- **Methods:**
  - `is_tight_day()`: Returns true if available time < 180 minutes
  - `to_prompt_str()`: Formats constraints as a string for AI/scheduler input

### DailyPlan
Represents a complete schedule for one day across all pets.
- **Attributes:** date, pets, constraints (DayConstraints), scheduled_tasks, skipped_tasks, conflicts (behavioral conflicts), time_conflicts (overlapping time windows)
- **Methods:**
  - `skipped_count()`: Return number of skipped tasks
  - `scheduled_count()`: Return number of scheduled tasks
  - `total_scheduled_minutes()`: Return total duration of all scheduled tasks
  - `is_valid()`: Return true if scheduled tasks fit within constraints
  - `add_task()`: Add a task to the plan (scheduled or skipped)
  - `get_tasks_for_pet()`: Return all tasks scheduled for a specific pet
  - `has_conflicts()`: Return true if any conflicts detected
  - `conflict_summary()`: Return human-readable summary of all conflicts

### Enumerations
- **TaskFrequency:** ONCE, DAILY, WEEKLY, MONTHLY
- **TaskStatus:** PENDING, COMPLETED, SKIPPED
- **TaskPriority:** LOW, MEDIUM, HIGH
- **TaskCategory:** WALK, FEED, GROOM, MEDICATION, PLAY, HEALTH_CHECK
- **EnergyLevel:** LOW, NORMAL, HIGH

## Relationships

- **Owner → Pet** (1:*): An owner manages multiple pets
- **Pet → Task** (1:*): Each pet has multiple tasks
- **Scheduler → Owner** (1:1): Scheduler works with an owner's account
- **Scheduler → DailyPlan** (→): Scheduler creates daily plans
- **DailyPlan → Pet** (1:*): One plan covers multiple pets
- **DailyPlan → DayConstraints** (1:1): A plan is created with specific day constraints
- **DailyPlan → Task** (1:*): A plan references multiple scheduled and skipped tasks
- **Task → Enums**: Task references TaskFrequency, TaskStatus, TaskPriority, and TaskCategory
- **DayConstraints → EnergyLevel**: Day constraints include energy level enum

## Design Rationale

✓ **Owner-centric model:** Owner manages all pets and tasks, providing a clear ownership hierarchy  
✓ **Multi-pet support:** One daily plan covers all pets, enabling coherent scheduling across all  
✓ **Recurrence handling:** Tasks automatically generate next occurrences when completed  
✓ **Time-aware scheduling:** Tasks support preferred times and duration, enabling conflict detection  
✓ **Flexible frequency:** Tasks support ONCE, DAILY, WEEKLY, MONTHLY frequencies with due dates  
✓ **Conflict detection:** System detects both behavioral conflicts (incompatible categories) and time-based conflicts (overlapping schedules)  
✓ **Status tracking:** Tasks track PENDING, COMPLETED, and SKIPPED states with proper state transitions

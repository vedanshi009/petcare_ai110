# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions that a user should be able to perform include adding multiple pets, remove pets and define recurring tasks for the pets like walking bathing etc.
- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Some objects in this system could be as follows:
Pet:
Attributes: id, name, species, age, health_notes, weight
Methods: age_label(), has_health_notes()
Task:
Attributes: id,name, category, priority, duration, non_negotiable
Methods: is_high_priority(), fits_in(minutes), summary()
DailyPlan:
Attributes: date, scheduled_tasks[],skipped_tasks[]
Methods: skipped_count(), scheduled_count()

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
I made some changes based on the AI feedback, some of them include:
1. Added DayConstraints relationship to DailyPlan which was missing earlier so that Scheduler can validate that scheduled tasks fit within available_minutes
2. Typed blocked_windows as list[Tuple[int, int]] instead of generic list as Scheduler needs to know exact structure to check time conflicts and as Generic list type is too vague and error-prone
3. Added two new methods: total_scheduled_minutes() and is_valid(), to prevent scheduler from creating plans that exceed available_minutes and enable early testing & debugging of scheduling logic

Later I made other changes, based on the main classes given in the instructions, so the code in the pawpal_systems.py file was restructured. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers several constraints when building daily plans:
- **Time availability**: Tasks must fit within the owner's available minutes for the day, accounting for blocked time windows
- **Task priority**: High-priority tasks are scheduled before medium or low priority ones
- **Non-negotiable flag**: Certain tasks must be scheduled regardless of time constraints
- **Preferred times**: Tasks with specific time preferences are prioritized accordingly
- **Task duration**: Each task has a fixed duration that must fit in remaining time
- **Recurring task frequency**: Only tasks due for the specific date are considered
- **Behavioral incompatibilities**: Some task combinations (back-to-back walks, PLAY/FEED too close together) are flagged as conflicts

I decided that priority and non-negotiable status mattered most because pet care involves critical health and safety needs that can't be skipped. Time constraints are secondary but still essential for realistic planning. Behavioral conflicts are treated as warnings rather than hard blocks, since they're based on general guidelines rather than absolute rules.

**b. Tradeoffs**
One tradeoff in the project is time budget instead of real time slots
The scheduler subtracts blocked windows from the total available time, but never checks whether a specific task's preferred time actually falls inside a blocked window. So a task set for 10:30am can still appear in the plan even if 9am–12pm is blocked.
This was a deliberate simplification, because  building a true timeline scheduler would have been a much bigger and more complex system to build. The budget approach is good enough for a first version, but it means the plan can be technically valid while still being practically wrong for the owner's actual day. The downside is that the plan can look slightly inconsistent: it respects how much time is blocked, but not which specific times are blocked.



## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

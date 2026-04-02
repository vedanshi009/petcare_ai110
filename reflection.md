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
I used AI tools to help explain what the code was doing, to improve and optimise the code for performance, help brainstorm ideas for new features and review and critique the code. 
- What kinds of prompts or questions were most helpful?
The prompts that were specific and to the point quesitons were most helpful as they gave efficient outputs. Also questions like "Give a critique of this code, say what responsibilities are missing or redundant."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment when I did not accept the suggestion was when I asked Copilot to review the code and optimize it and make it more efficient for performance and space. It gave a complicated version of a simple algorithm that was harder to grasp and unneccessarily long, so I rejected that output.

- How did you evaluate or verify what the AI suggested?
By going through the code and understanding it myself, or by asking it to review it again.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
Task completion status changes, adding tasks to pets, priority logic, scheduler time budgeting, and filtering tasks by status and pet name.
- Why were these tests important?
These are the core actions the app depends on — if any of them silently break, the entire daily plan becomes wrong without any visible error.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Confident for normal cases but less confident around edge cases. 
- What edge cases would you test next if you had more time?
I would test tasks that together exceed the available time, and a recurring task completing on the last day of a month.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The recurring task logic, create_next_occurrence() using timedelta feels like a genuinely useful real-world feature, not just an exercise.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Replace the greedy scheduler with one that reserves time for non-negotiable tasks first before filling the rest, so critical tasks can never get bumped.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI is useful when you already know what you want to build, but asking it to design something from scratch produces code you don't fully understand or trust.

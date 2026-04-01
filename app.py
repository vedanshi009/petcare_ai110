import streamlit as st
from datetime import date
from uuid import uuid4
from pawpal_system import (
    Owner,
    Pet,
    Task,
    TaskCategory,
    TaskPriority,
    TaskFrequency,
    TaskStatus,
    DayConstraints,
    EnergyLevel,
    Scheduler,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize owner and pet in session_state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, owner_id=str(uuid4())[:8])

if "pet" not in st.session_state:
    st.session_state.pet = Pet(
        id=str(uuid4())[:8],
        name=pet_name,
        species=species,
        age=3,
        weight=10.0
    )
    st.session_state.owner.add_pet(st.session_state.pet)

# Update pet info if inputs changed
st.session_state.pet.name = pet_name
st.session_state.pet.species = species
st.session_state.owner.name = owner_name

st.markdown("### Add Task")
col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    priority_enum = TaskPriority[priority.upper()]
    task = Task(
        id=str(uuid4())[:8],
        name=task_title,
        description=f"Task for {pet_name}",
        category=TaskCategory.PLAY,  # Default category
        priority=priority_enum,
        duration=int(duration),
        pet_id=st.session_state.pet.id,
        frequency=TaskFrequency.DAILY
    )
    st.session_state.pet.add_task(task)
    st.success(f"✓ Added '{task_title}' to {pet_name}'s tasks")

# Display current tasks
if st.session_state.pet.task_count() > 0:
    st.write(f"**Tasks for {pet_name}:**")
    for task in st.session_state.pet.tasks:
        st.caption(f"• {task.name} ({task.duration}min, {task.priority.value})")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

col1, col2 = st.columns(2)
with col1:
    available_minutes = st.slider("Available time (minutes)", 60, 480, 240)
with col2:
    energy = st.selectbox("Pet energy level", ["low", "normal", "high"], index=1)

if st.button("Generate schedule"):
    # Create constraints for the day
    energy_enum = EnergyLevel[energy.upper()]
    constraints = DayConstraints(
        available_minutes=available_minutes,
        energy_level=energy_enum,
        special_notes=f"Scheduled for {st.session_state.owner.name}'s {st.session_state.pet.name}"
    )

    # Build the schedule using Scheduler
    scheduler = Scheduler(st.session_state.owner)
    plan = scheduler.build_plan(date.today(), constraints)

    # Display results
    st.success(f"✓ Schedule generated for {date.today().strftime('%A, %B %d, %Y')}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Available", f"{available_minutes} min")
    with col2:
        st.metric("Scheduled", f"{plan.scheduled_count()} tasks • {plan.total_scheduled_minutes()} min")
    with col3:
        remaining = available_minutes - plan.total_scheduled_minutes()
        st.metric("Remaining", f"{remaining} min")

    st.divider()

    # Show scheduled tasks
    if plan.scheduled_tasks:
        st.subheader(f"Today's Plan ({plan.scheduled_count()} tasks)")
        for task in plan.scheduled_tasks:
            status_icon = "✓" if task.non_negotiable else " "
            st.write(f"**{status_icon} {task.name}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"⏱ {task.duration} min")
            with col2:
                st.caption(f"Priority: {task.priority.value}")
            with col3:
                st.caption(f"Category: {task.category.value}")
    else:
        st.info("No tasks fit in the available time.")

    # Show deferred tasks
    if plan.skipped_tasks:
        st.subheader(f"Couldn't fit ({plan.skipped_count()} tasks)")
        for task in plan.skipped_tasks:
            st.write(f"• {task.name} ({task.duration} min) — {task.priority.value} priority")

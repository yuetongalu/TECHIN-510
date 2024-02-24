import sqlite3
import streamlit as st
from pydantic import BaseModel
from pydantic import ValidationError
#import streamlit_pydantic as sp
import os

# Database setup
DB_PATH = "todoapp.sqlite"
con = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = con.cursor()

# Create the tasks table if it doesn't exist
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        is_done BOOLEAN NOT NULL CHECK (is_done IN (0, 1))
    )
    """
)

# Pydantic model for Task
class Task(BaseModel):
    name: str
    description: str
    is_done: bool

# Function to toggle the completion status of a task
def toggle_is_done(task_id: int, is_done: bool):
    cur.execute("UPDATE tasks SET is_done = ? WHERE id = ?", (is_done, task_id))
    con.commit()

# Function to display and handle the task editing form
def edit_task_form(task_id: int):
    task = cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task:
        with st.form("edit_task"):
            name = st.text_input("Name", value=task[1])
            description = st.text_area("Description", value=task[2])
            is_done = st.checkbox("Done", value=bool(task[3]))
            submitted = st.form_submit_button("Update Task")
            if submitted:
                cur.execute("UPDATE tasks SET name = ?, description = ?, is_done = ? WHERE id = ?", (name, description, is_done, task_id))
                con.commit()
                st.success("Task updated successfully!")
                st.button("Back to task list", on_click=lambda: st.experimental_rerun())


def main():
    st.title("Todo App")

    # Check for edit query parameter
    task_id = st.experimental_get_query_params().get("edit")
    if task_id:
        edit_task_form(int(task_id[0]))
        return
with st.form("task_form"):
    name = st.text_input("Name")
    description = st.text_area("Description")
    is_done = st.checkbox("Done")
    submitted = st.form_submit_button("Add Task")

    if submitted:
        try:
            # Validate data using Pydantic
            task = Task(name=name, description=description, is_done=is_done)
            # Insert validated task into the database
            cur.execute("INSERT INTO tasks (name, description, is_done) VALUES (?, ?, ?)", (task.name, task.description, task.is_done))
            con.commit()
            st.success("Task added successfully!")
        except ValidationError as e:
            st.error(f"Error adding task: {e}")

    # Display tasks
    tasks = cur.execute("SELECT * FROM tasks").fetchall()
    for task in tasks:
        cols = st.columns([0.1, 1, 2, 0.1])
        is_done = cols[0].checkbox("", task[3], key=f"done_{task[0]}")
        cols[1].write(task[1])
        cols[2].write(task[2])
        edit_button = cols[3].button("Edit", key=f"edit_{task[0]}")
        if edit_button:
            # Redirect to edit form with task ID as query parameter
            st.experimental_set_query_params(edit=task[0])
            st.experimental_rerun()

    if st.button('Update Task Statuses'):
        for task in tasks:
            is_done = st.session_state.get(f"done_{task[0]}", task[3])
            if is_done != task[3]:  # Check if the status has been toggled
                toggle_is_done(task[0], is_done)
    # # Task creation form
    # with st.form("task_form", clear_on_submit=True):
    #     data = sp.pydantic_form_body(model=Task)
    #     submitted = st.form_submit_button("Add Task")
    #     if submitted and data:
    #         cur.execute("INSERT INTO tasks (name, description, is_done) VALUES (?, ?, ?)", (data.name, data.description, data.is_done))
    #         con.commit()
    #         st.success("Task added successfully!")

    # Display tasks
    tasks = cur.execute("SELECT * FROM tasks").fetchall()
    for task in tasks:
        cols = st.columns([0.1, 1, 2, 0.1])
        done = cols[0].checkbox("", task[3], key=f"done_{task[0]}", on_change=toggle_is_done, args=(task[0], not task[3]))
        cols[1].write(task[1])
        cols[2].write(task[2])
        edit_button = cols[3].button("Edit", key=f"edit_{task[0]}")
        if edit_button:
            # Redirect to edit form with task ID as query parameter
            st.experimental_set_query_params(edit=task[0])
            st.experimental_rerun()

if __name__ == "__main__":
    main()
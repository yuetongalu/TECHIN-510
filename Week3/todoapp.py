import streamlit as st
import sqlite3
from pydantic import BaseModel

# Initialize database connection
DB_PATH = "todoapp.sqlite"
con = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = con.cursor()

# Create tasks table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        is_done BOOLEAN NOT NULL CHECK (is_done IN (0, 1))
    )
""")

# Pydantic model for a task
class Task(BaseModel):
    name: str
    description: str
    is_done: bool = False

# Function to update a task
def update_task(task_id: int, name: str, description: str, is_done: bool):
    cur.execute("UPDATE tasks SET name = ?, description = ?, is_done = ? WHERE id = ?", (name, description, is_done, task_id))
    con.commit()

# Toggle task completion status
def toggle_is_done(task_id: int, is_done: bool):
    cur.execute("UPDATE tasks SET is_done = ? WHERE id = ?", (is_done, task_id))
    con.commit()

# Main app function
def main():
    st.title("Todo App")

    # Handle task editing if 'edit' parameter is present
    task_id_to_edit = st.experimental_get_query_params().get("edit")
    if task_id_to_edit:
        task_id_to_edit = int(task_id_to_edit[0])
        task_to_edit = cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id_to_edit,)).fetchone()
        if task_to_edit:
            st.subheader("Edit Task")
            with st.form("edit_task"):
                name = st.text_input("Name", value=task_to_edit[1])
                description = st.text_area("Description", value=task_to_edit[2])
                is_done = st.checkbox("Done", value=task_to_edit[3])
                submitted = st.form_submit_button("Update Task")
                if submitted:
                    update_task(task_id_to_edit, name, description, is_done)
                    st.experimental_set_query_params()  # Clear query params
                    st.experimental_rerun()

    # Task creation form
    with st.form("task_form"):
        name = st.text_input("Name")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Add Task")
        if submitted and name:  # Ensuring that 'name' is not empty
            task = Task(name=name, description=description)
            cur.execute("INSERT INTO tasks (name, description, is_done) VALUES (?, ?, ?)", (task.name, task.description, task.is_done))
            con.commit()
            st.success("Task added successfully!")

    # Display tasks with an option to toggle completion and edit
    st.subheader("Tasks")
    tasks = cur.execute("SELECT * FROM tasks").fetchall()
    for task in tasks:
        cols = st.columns([0.1, 1, 2, 0.1])
        cols[0].checkbox("", task[3], key=f"done_{task[0]}", on_change=toggle_is_done, args=(task[0], not task[3]))
        cols[1].write(task[1])
        cols[2].write(task[2])
        edit_button = cols[3].button("Edit", key=f"edit_{task[0]}")

        if edit_button:
            # Redirect to edit form with task ID as a query parameter
            st.experimental_set_query_params(edit=task[0])
            st.experimental_rerun()

if __name__ == "__main__":
    main()

import streamlit as st
import httpx

API = "http://localhost:8000"

st.set_page_config(page_title="Task Manager", page_icon="📋", layout="wide")
st.title("📋 Task Manager Dashboard")

# -------- Helpers --------
def api_get(path):
    try:
        r = httpx.get(API + path, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API GET error: {e}")
        return None

def api_post(path, data):
    try:
        r = httpx.post(API + path, json=data, timeout=5)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        st.error(f"API POST error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"API POST error: {e}")
        return None

def api_patch(path):
    try:
        r = httpx.patch(API + path, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API PATCH error: {e}")
        return None

# -------- Tabs --------
tab_users, tab_create_task, tab_tasks = st.tabs(
    ["👤 Users", "➕ Create Task", "📝 Task Board"]
)

# =======================
# 👤 Users
# =======================
with tab_users:
    st.subheader("Create User")

    with st.form("create_user_form"):
        name = st.text_input("Name")
        role = st.selectbox("Role", ["admin", "manager", "team member"])
        email = st.text_input("Email")
        phone = st.text_input("Phone (optional)")
        submit_user = st.form_submit_button("Create User")

    if submit_user:
        if not name or not email:
            st.warning("Name and Email are required")
        else:
            payload = {
                "name": name,
                "role": role,
                "profile": {
                    "email": email,
                    "phone": phone if phone else None
                }
            }
            res = api_post("/users/", payload)
            if res:
                st.success("User created successfully")

    st.divider()
    st.subheader("All Users")

    users = api_get("/users/")
    if users is not None:
        if len(users) == 0:
            st.info("No users yet")
        else:
            st.table(users)

# =======================
# ➕ Create Task
# =======================
with tab_create_task:
    st.subheader("Create Task")

    users = api_get("/users/") or []
    user_map = {u["id"]: u["name"] for u in users}

    with st.form("create_task_form"):
        title = st.text_input("Title (Must start with capital letter)")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", ["low", "medium", "high"])
        status = st.selectbox("Status", ["pending", "in_progress", "completed"])
        assigned_to = st.selectbox(
            "Assign To",
            [None] + list(user_map.keys()),
            format_func=lambda x: user_map.get(x, "None")
        )
        submit_task = st.form_submit_button("Create Task")

    if submit_task:
        if not title or not description:
            st.warning("Title and Description are required")
        else:
            payload = {
                "title": title,
                "description": description,
                "priority": priority,
                "status": status,
                "assigned_to": assigned_to
            }
            res = api_post("/tasks/", payload)
            if res:
                st.success("Task created successfully")

# =======================
# 📝 Task Board
# =======================
with tab_tasks:
    st.subheader("All Tasks")

    tasks = api_get("/tasks/")
    if tasks is not None:
        if len(tasks) == 0:
            st.info("No tasks found")
        else:
            for task in tasks:
                with st.container(border=True):
                    st.markdown(f"### {task['title']}")
                    st.write(task["description"])
                    st.caption(
                        f"Priority: {task['priority']} | "
                        f"Status: {task['status']} | "
                        f"Assigned to: {task['assigned_to']}"
                    )

                    new_status = st.selectbox(
                        "Update Status",
                        ["pending", "in_progress", "completed"],
                        index=["pending", "in_progress", "completed"].index(task["status"]),
                        key=f"status_{task['id']}"
                    )

                    if st.button("Update Status", key=f"update_{task['id']}"):
                        res = api_patch(
                            f"/tasks/{task['id']}/status?status_update={new_status}"
                        )
                        if res:
                            st.success("Status updated")
                            st.rerun()
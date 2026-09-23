import streamlit as st
import pandas as pd
from db import get_all_users, update_user, delete_user
from datetime import datetime, date
st.set_page_config(page_title="Edit Page", layout="wide")
if not st.user.is_logged_in:
    st.warning("Please log in from the main page to access this page.")
    st.stop()
with st.expander("ℹ️ How to Use This Page", expanded=True):
    st.markdown("""
    1. **Select a Member:** Choose the user you want to modify from the **Select User to Edit** dropdown.
    2. **Edit Details:** Update any field (Name, Date of Birth, or Gender) inside the form below. 
    3. **Save Updates:** Click **💾 Save Changes** to write your updates directly to the database.
    4. **Delete a Member:** Click **🗑️ Delete This Record** at the bottom, then confirm to permanently remove the user.
    """)

users = get_all_users()

if not users:
    st.warning("No users were found")
else:
    user_options = {
        f"ID {u['ID']}: {u['First Name']} {u['Last Name']}": u
        for u in users
    }
    selected_label = st.selectbox("Select User", list(user_options.keys()))
    selected_user = user_options[selected_label]

    try:
        default_dob = datetime.strptime(selected_user["Date of Birth"], "%Y-%m-%d").date()
    except ValueError:
        default_dob = date(2000, 1, 1)

    with st.form("edit user form"):
        col1, col2 = st.columns(2)
        with col1:
            new_first = st.text_input("First Name", value=selected_user["First Name"])
        with col2:
            new_last = st.text_input("Last Name", value=selected_user["Last Name"])

        col3, col4 = st.columns(2)
        with col3:
            new_dob = st.date_input("Date of Birth", value=default_dob, min_value=date(1900, 1, 1), max_value=date.today())
        with col4:
            gender_options = ["Male", "Female"]
            current_gender_idx = gender_options.index(selected_user["Gender"]) if selected_user["Gender"] in gender_options else 0
            new_gender = st.selectbox("Gender", gender_options, index=current_gender_idx)
        save_submitted = st.form_submit_button("Save Changes")

    if save_submitted:
        if new_first.strip() and new_last.strip():
            update_user(
                selected_user["ID"],
                new_first.strip(),
                new_last.strip(),
                new_dob,
                new_gender
            )
            st.success("User Updated")
            st.rerun()
        else:
            st.error("entries can't be empty")

    with st.popover("🗑️ Delete This Record"):
        st.write(f"Are you sure you want to permanently delete **{selected_user['First Name']} {selected_user['Last Name']}**?")
        if st.button("Confirm Delete", type="primary"):
            delete_user(selected_user["ID"])
            st.success("User deleted successfully!")
            st.rerun()
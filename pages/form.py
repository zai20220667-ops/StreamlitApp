import streamlit as st
from db import insert_user
from datetime import date
if not st.session_state.get("authentication_status"):
    st.warning("Please log in from the main page to access this page.")
    st.stop()
st.title("WELCOME TO INPUT PAGE")

with st.form("user_input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("Enter your first name")
    with col2:
        last_name = st.text_input("Enter your last name")
    col3, col4 = st.columns(2)
    with col3:
        DOB=st.date_input("Enter your DOB",value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
    with col4:
        gender = st.selectbox("Select your gender", ["Male", "Female"])
    submitted = st.form_submit_button("Submit Entry", type="primary")

if submitted:
    if first_name.strip() and last_name.strip():
        insert_user(first_name.strip(), last_name.strip(), DOB, gender)
        st.success(f"Registered {first_name.strip()} {last_name.strip()} in SQLite!")
    else:
        st.error("Please enter both your first name and last name.")
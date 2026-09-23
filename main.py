import streamlit as st
from db import init_db

st.title("WELCOME TO HOME PAGE")
st.write("use the sidebar to navigate to Input or Display pages")
init_db()

if not st.user.is_logged_in:
    st.write("Please log in to continue.")
    if st.button("Log in"):
        st.login()
    st.stop()

st.sidebar.write(f"Signed in as **{st.user.get('preferred_username', st.user.name)}**")
if st.sidebar.button("Log out"):
    st.logout()
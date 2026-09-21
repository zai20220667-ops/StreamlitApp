import streamlit as st
import pandas as pd
from db import get_all_users, update_user, delete_user

st.set_page_config(page_title="Display Dashboard", layout="wide")
if not st.session_state.get("authentication_status"):
    st.warning("Please log in from the main page to access this page.")
    st.stop()
st.title("Display Page")

user = get_all_users()
if not user:
    st.info("No name entered yet.")
else:
    latest_user = user[-1]
    latest_name_str = f"{latest_user['First Name']} {latest_user['Last Name']}"
    col1, col2 = st.columns(2)
    col1.metric("Total Registered", len(user))
    col2.metric("Latest Member", latest_name_str)

    st.divider()
    st.subheader("Entries:")

    df = pd.DataFrame(user)
    df.index += 1

    st.dataframe(
        df,
        column_config={"First Name": st.column_config.TextColumn("First Name"),
            "Last Name": st.column_config.TextColumn("Last Name"),
            "Date of Birth": st.column_config.DateColumn("Date of Birth", format="YYYY-MM-DD"),
            "Gender": st.column_config.TextColumn("Gender")
        }
    )
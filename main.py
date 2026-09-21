import os
import streamlit as st
import streamlit_authenticator as stauth
from db import init_db, get_authenticator_credentials

st.title("WELCOME TO HOME PAGE")
st.write("use the sidebar to navigate to Input or Display pages")
init_db()
credentials = get_authenticator_credentials()
authenticator = stauth.Authenticate(
    credentials,
    cookie_name="auth cookie",
    key=os.environ["COOKIE_KEY"],
    cookie_expiry_days=30,
)
authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()
elif st.session_state["authentication_status"] is False:
    st.error("Authentication Failed")
elif st.session_state["authentication_status"] is None:
    st.warning("please enter username and password")
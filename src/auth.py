import streamlit as st
from .auth_utils import hash_password, verify_password, core_login_user, core_register_user, is_password_strong

def login_user(email, password):
    success, user = core_login_user(email, password)
    if success and user:
        st.session_state['logged_in'] = True
        st.session_state['email'] = email
        st.session_state['name'] = user.get('name', email)
        return True
    return False

def register_user(name, email, password):
    return core_register_user(name, email, password)

def require_auth():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Please Log in to access the Dashboard.")
        st.stop()

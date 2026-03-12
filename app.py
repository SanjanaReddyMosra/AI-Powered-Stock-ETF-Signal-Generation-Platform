import streamlit as st
from src.auth import login_user, register_user

st.set_page_config(page_title="AI Stock Signals", layout="centered", page_icon="📈")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.switch_page("pages/1_Dashboard.py")
        
    st.markdown("<h1 style='text-align: center;'>AI-Powered Stock Signals</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Login or Register to access the 10-Stock dashboard.</p>", unsafe_allow_html=True)
    st.write("")

    # Custom CSS for a nicer look
    st.markdown("""
        <style>
        .stTextInput>div>div>input {
            border-radius: 8px;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            border-color: #00E676;
            color: #00E676;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])
        
        with tab1:
            st.write("### Sign In to Your Account")
            email = st.text_input("Email Address", key="login_email")
            pwd = st.text_input("Password", type="password", key="login_pwd")
            if st.button("Login", use_container_width=True, type="primary"):
                if login_user(email, pwd):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")
                    
        with tab2:
            st.write("### Create a New Account")
            new_name = st.text_input("Full Name", key="reg_name", help="How should we refer to you?")
            new_email = st.text_input("Email Address", key="reg_email")
            new_pwd = st.text_input("Password", type="password", key="reg_pwd", help="Min 6 chars, 1 uppercase, 1 lowercase, 1 number, 1 symbol.")
            if st.button("Register", use_container_width=True, type="primary"):
                if not new_name or not new_email or not new_pwd:
                    st.warning("Please fill out all fields.")
                elif "@" not in new_email:
                    st.warning("Please enter a valid email address.")
                else:
                    success, msg = register_user(new_name, new_email, new_pwd)
                    if success:
                        st.success(msg + ". You can now log in.")
                    else:
                        st.error(msg)

if __name__ == "__main__":
    main()

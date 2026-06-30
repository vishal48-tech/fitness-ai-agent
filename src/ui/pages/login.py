# src/ui/pages/login.py
"""
Login and registration view using Supabase Auth.
"""
import streamlit as st
from src.auth.auth_manager import AuthManager

def render_login_page():
    st.title("💪 AI Fitness Coach V2")
    st.subheader("Achieve your fitness goals with personalized AI-guided coaching.")

    # Tabs for login, registration, and Google OAuth
    # tab_login, tab_register, tab_google = st.tabs(["🔑 Login", "📝 Sign Up", "🌐 Google OAuth"])
    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab_login:
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In", use_container_width=True):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    res = AuthManager.sign_in(email, password)
                    if res.session and res.user:
                        st.session_state["supabase_session"] = res.session
                        st.session_state["supabase_user"] = res.user
                        st.success("Successfully logged in!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

    with tab_register:
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        display_name = st.text_input("Display/Nick Name (Optional)", key="reg_name")
        if st.button("Register Account", use_container_width=True):
            if not reg_email or not reg_password:
                st.error("Please enter email and password.")
            elif len(reg_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    res = AuthManager.sign_up(reg_email, reg_password, display_name)
                    st.success("Sign up successful! Please check your email or log in directly.")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")

    # with tab_google:
    #     st.write("Or instantly connect using your Google Account:")
    #     if st.button("Log in with Google", use_container_width=True):
    #         try:
    #             auth_url = AuthManager.get_google_auth_url()
    #             if auth_url:
    #                 st.session_state["redirect_url"] = auth_url
    #                 st.rerun()
    #         except Exception as e:
    #             st.error(f"Failed to trigger OAuth redirect: {str(e)}")

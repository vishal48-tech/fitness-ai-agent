# app.py
"""
AI Fitness Coach V2 - Entry point.
Implements routing between Login, Dashboard, Chat, and Workout Logging views.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from src.auth.supabase_client import get_supabase


# Load configurations
load_dotenv()

from src.ui.pages.login import render_login_page
from src.ui.pages.dashboard import render_dashboard
from src.ui.pages.chat import render_chat_page
from src.ui.pages.workout_log import render_workout_log_page
from src.ui.components.sidebar import render_sidebar
from config.settings import (
    PAGE_TITLE, PAGE_ICON, GROQ_MODELS, GROQ_MODEL
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up page configurations
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup basic styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Handle instant redirects at the root document level to bypass iframe sandboxing
    if "redirect_url" in st.session_state:
        url = st.session_state.pop("redirect_url")
        st.markdown(
            f"""
            <meta http-equiv="refresh" content="0; url={url}">
            <script>
                window.top.location.href = "{url}";
            </script>
            Redirecting to login...
            """,
            unsafe_allow_html=True
        )
        st.stop()

    # OAuth Callback handling: Check query/hash parameters from Supabase redirect
    # Streamlit query params exposes parameters sent back in the URL
    params = st.query_params
    
    # If the URL contains access token hash fragments, convert them to query parameters for Python
    st.markdown(
        """
        <script>
            (function() {
                // Get the current URL
                var url = window.top.location.href || window.location.href;
                
                // Check if there's a hash with access_token
                if (url.includes('#') && url.includes('access_token')) {
                    // Convert hash to query params
                    var hash = url.split('#')[1];
                    var cleanUrl = url.split('#')[0];
                    window.top.location.replace(cleanUrl + '?' + hash);
                }
            })();
            </script>
        """,
        unsafe_allow_html=True
    )


    if "code" in params:
        # User is returning from OAuth provider
        logger.info(f"{params}")
        supabase = get_supabase()
        try:
            # Reconstruct session details from query parameters
            code = params.get("code")
            
            # In gotrue-py, set_session can take the tokens directly
            session = supabase.auth.set_session({"access_token": code, "refresh_token": code})


            if session and hasattr(session, "user") and session.user:
                st.session_state["supabase_session"] = session
                st.session_state["supabase_user"] = session.user
                # Clean up parameters from state
                st.query_params.clear()
                st.rerun()
            else:
                st.warning("Session returned but no user details found.")
        except Exception as e:
            st.error(f"Error during OAuth session exchange: {str(e)}")
            # Log full stack trace
            import traceback
            st.code(traceback.format_exc())
            # Don't silence it so we can see the exact cause
            st.stop()

    # Verify API credentials exist
    if not os.getenv("GROQ_API_KEY"):
        st.warning("⚠️ Please set your GROQ_API_KEY in the .env file")
        st.info("Get an API key at https://console.groq.com")
        return

    # Check for authentication state
    user = st.session_state.get("supabase_user")

    if not user:
        render_login_page()
    else:
        # Render common sidebar controls
        render_sidebar()

        # Multi-page routing selector
        page_selection = st.radio(
            "Go to:",
            ["Dashboard", "AI Coach Chat", "Log Workout"],
            horizontal=True
        )

        st.markdown("---")

        if page_selection == "Dashboard":
            render_dashboard()
        elif page_selection == "AI Coach Chat":
            render_chat_page()
        elif page_selection == "Log Workout":
            render_workout_log_page()

if __name__ == "__main__":
    main()
# src/ui/components/sidebar.py
"""
Shared sidebar component for navigation and session actions.
"""
import streamlit as st
import os
from src.auth.supabase_client import get_supabase
from src.database.db_manager import DBManager

def render_sidebar():
    """Renders the common sidebar controls and navigation hooks."""
    with st.sidebar:
        st.title("💪 AI Fitness Coach")
        st.caption("V2.0.0 | Multi-User Edition")
        st.markdown("---")

        user = st.session_state.get("supabase_user")
        if not user:
            st.warning("Please login to access all features.")
            return

        # Fetch profile info
        profile = DBManager.get_or_create_profile(
            user.id, 
            email=user.email, 
            user_metadata=getattr(user, "user_metadata", None)
        )
        display_name = profile.get("display_name")
        if not display_name or "@" in display_name:
            # Fallback to cleaned prefix of email if name is empty or looks like an email
            display_name = user.email.split("@")[0].capitalize()
        
        st.subheader(f"👤 Welcome, {display_name}!")
        
        st.markdown("---")

        # Session Stats
        st.subheader("📊 Current Session")
        st.metric("Model", "Llama 3.3 70B")
        
        st.markdown("---")

        # Logout button
        if st.button("🚪 Sign Out", use_container_width=True):
            session = st.session_state.get("supabase_session")
            if session:
                supabase = get_supabase()
                try:
                    supabase.auth.sign_out()
                except Exception:
                    pass
            
            # Clear all session state keys
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            st.success("Signed out successfully!")
            st.rerun()

# src/ui/pages/dashboard.py
"""
User dashboard for displaying fitness stats and updating profiles.
"""
import streamlit as st
from src.database.db_manager import DBManager

def render_dashboard():
    user = st.session_state.get("supabase_user")
    if not user:
        st.error("No active user session. Please sign in.")
        return

    # Load existing user profile
    profile = DBManager.get_or_create_profile(
        user.id, 
        email=user.email, 
        user_metadata=getattr(user, "user_metadata", None)
    )
    display_name = profile.get("display_name")
    if not display_name or "@" in display_name:
        display_name = user.email.split("@")[0].capitalize()

    st.title(f"🏋️ {display_name}'s Fitness Dashboard")
    st.markdown("Monitor your goals, available equipment, and fitness metrics here.")

    st.markdown("---")

    # Goals and Info Display Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Current Level", value=profile.get("fitness_level", "beginner").capitalize())
    with col2:
        st.metric(label="Logged Workouts", value=len(DBManager.get_workout_logs(user.id)))
    with col3:
        st.metric(label="Preferred Equipment", value=profile.get("equipment") or "Bodyweight")

    st.markdown("---")

    # Expandable edit profile section
    st.subheader("🎯 Configure Your Fitness Profile")
    with st.form("profile_form"):
        new_name = st.text_input("Name/Nickname", value=profile.get("display_name") or "")
        new_goals = st.text_area("What are your fitness goals?", value=profile.get("goals") or "")
        new_limitations = st.text_area("Injuries or training limitations?", value=profile.get("limitations") or "")
        new_level = st.select_slider(
            "Fitness Level",
            options=["beginner", "intermediate", "advanced"],
            value=profile.get("fitness_level") or "beginner"
        )
        
        equipment_options = [
            "None/Bodyweight", "Dumbbells", "Barbell", "Resistance Bands",
            "Kettlebell", "Pull-up Bar", "Treadmill", "Exercise Bike"
        ]
        
        existing_equip = [e.strip() for e in (profile.get("equipment") or "").split(",") if e.strip()]
        new_equip = st.multiselect(
            "Available Equipment",
            options=equipment_options,
            default=[e for e in existing_equip if e in equipment_options] or ["None/Bodyweight"]
        )

        if st.form_submit_button("Save Profile Settings"):
            equipment_str = ", ".join(new_equip)
            DBManager.update_profile(
                user_id=user.id,
                goals=new_goals,
                limitations=new_limitations,
                equipment=equipment_str,
                fitness_level=new_level,
                display_name=new_name
            )
            st.success("Your profile has been saved successfully!")
            st.rerun()

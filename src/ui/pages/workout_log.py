# src/ui/pages/workout_log.py
"""
Workout Logging interface.
Log new sessions and view log history.
"""
import streamlit as st
from src.database.db_manager import DBManager

def render_workout_log_page():
    user = st.session_state.get("supabase_user")
    if not user:
        st.error("Please login to log workouts.")
        return

    st.title("💪 Workout Logger")
    st.markdown("Record your training sessions to track progress.")

    tab_log, tab_history = st.tabs(["📝 Log Workout", "📅 History"])

    with tab_log:
        with st.form("workout_form"):
            workout_type = st.selectbox(
                "Workout Type",
                ["Strength Training", "Cardio", "HIIT", "Flexibility", "Yoga", "Other"]
            )
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
            difficulty = st.selectbox("Difficulty", ["easy", "moderate", "hard"])
            notes = st.text_area("Exercises and Notes", placeholder="e.g. Squat 3x5, Bench Press 3x5...")

            if st.form_submit_button("Record Workout"):
                DBManager.log_workout(
                    user_id=user.id,
                    workout_type=workout_type,
                    duration=duration,
                    difficulty=difficulty,
                    notes=notes
                )
                st.success("Workout recorded successfully!")
                st.balloons()

    with tab_history:
        logs = DBManager.get_workout_logs(user.id, limit=20)
        if not logs:
            st.info("No workouts logged yet. Start training today!")
        else:
            for log in logs:
                st.markdown(f"### {log['workout_type']} — {log['duration']} mins")
                st.markdown(f"**Date:** {log['logged_at'][:10]} | **Difficulty:** {log['difficulty'].capitalize()}")
                if log.get("notes"):
                    st.info(log["notes"])
                st.markdown("---")

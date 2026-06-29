# src/ui/pages/chat.py
"""
AI Fitness Coach Chat Interface.
Supports interactive multi-session chats, streaming outputs, and DB saving.
"""
import streamlit as st
import os
import time
from src.database.db_manager import DBManager
from src.agent.fitness_agent import GroqFitnessAgent

def render_chat_page():
    user = st.session_state.get("supabase_user")
    if not user:
        st.error("Please login to start a coaching chat.")
        return

    st.title("💪 AI Coaching Assistant")
    st.caption("Ask questions, build programs, or check nutrition plans.")

    # 1. Session Picker
    sessions = DBManager.get_chat_sessions(user.id)
    session_titles = ["Create New Session"] + [s.get("title") or "Unnamed Session" for s in sessions]
    selected_index = st.selectbox("Select Chat Conversation:", range(len(session_titles)), index=0)

    # 2. Session ID Management
    active_session_id = None
    if selected_index == 0:
        if st.button("🆕 Start New Session"):
            new_session = DBManager.create_chat_session(user.id, f"Session {time.strftime('%b %d, %H:%M')}")
            st.session_state["active_session_id"] = new_session.get("id")
            st.success("New session started!")
            st.rerun()
    else:
        active_session_id = sessions[selected_index - 1].get("id")
        st.session_state["active_session_id"] = active_session_id

    active_session_id = st.session_state.get("active_session_id")
    if not active_session_id:
        st.info("Select an existing conversation or click 'Start New Session' above.")
        return

    # 3. Load Chat History
    messages = DBManager.get_chat_messages(active_session_id)
    
    # Render historical messages
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 4. Handle input
    if prompt := st.chat_input("Ask your coach..."):
        # Save user message
        DBManager.save_chat_message(active_session_id, user.id, "user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate agent response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Initialize agent
            agent = GroqFitnessAgent(
                user_id=user.id,
                groq_api_key=os.getenv("GROQ_API_KEY", "")
            )
            
            # Fetch user profile for context injection
            profile = DBManager.get_or_create_profile(user.id, user.email)
            
            # Format history for agent
            chat_history_formatted = [{"role": m["role"], "content": m["content"]} for m in messages]

            # Stream output
            response_chunks = []
            for chunk in agent.chat_stream(prompt, chat_history_formatted, profile):
                response_chunks.append(chunk)
                message_placeholder.markdown("".join(response_chunks) + "▌")
            
            full_response = "".join(response_chunks)
            message_placeholder.markdown(full_response)
            
            # Save assistant message to Supabase
            DBManager.save_chat_message(active_session_id, user.id, "assistant", full_response)

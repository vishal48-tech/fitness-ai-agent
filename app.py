# app.py
"""
AI Fitness Coach - Powered by Groq + LangChain
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent))


from src.agent.fitness_agent import GroqFitnessAgent
from config.settings import (
    PAGE_TITLE, PAGE_ICON, GROQ_MODELS, GROQ_MODEL
)
import os
from dotenv import load_dotenv

load_dotenv()

# Create data directory if it doesn't exist
os.makedirs("./chroma_data", exist_ok=True)


# Page config
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
        <style>
        /* Modern chat styling */
        .stChatMessage {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        /* User message */
        [data-testid="stChatMessage"]:has(.stChatMessageAvatar:first-child) {
            background-color: #2b313e;
        }
        
        /* Assistant message */
        [data-testid="stChatMessage"]:has(.stChatMessageAvatar:last-child) {
            background-color: #1e2330;
            border-left: 4px solid #667eea;
        }
        
        /* Workout card */
        .workout-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 10px 0;
            color: white;
        }
        
        /* Progress bar */
        .progress-section {
            background-color: #2b313e;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        /* Quick action buttons */
        .quick-action-btn {
            background-color: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            border: none;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .quick-action-btn:hover {
            transform: scale(1.05);
        }
        
        /* Groq speed indicator */
        .speed-indicator {
            background-color: #1e2330;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
            margin: 5px 0;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session():
    """Initialize all session state variables"""
    if 'agent_initialized' not in st.session_state:
        # Check for API key
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not groq_api_key:
            st.error("⚠️ GROQ_API_KEY not found!")
            st.info("Get your API key from https://console.groq.com")
            st.code("Add GROQ_API_KEY=your_key_here to .env file")
            st.stop()
        
        # Initialize agent
        st.session_state.agent = GroqFitnessAgent(
            user_id=st.session_state.get('user_id', 'default'),
            groq_api_key=groq_api_key,
            model_name=GROQ_MODEL
        )
        
        st.session_state.agent_initialized = True
        st.session_state.messages = []
        st.session_state.model_name = GROQ_MODEL
        st.session_state.start_time = time.time()
        st.session_state.total_tokens = 0
    
    if 'user_id' not in st.session_state:
        import uuid
        st.session_state.user_id = str(uuid.uuid4())

# Sidebar
def render_sidebar():
    with st.sidebar:
        st.title("💪 AI Fitness Coach")
        st.markdown("---")
        
        # Model selection
        st.subheader("🤖 Model Settings")
        
        model_display_names = list(GROQ_MODELS.keys())
        current_model_index = list(GROQ_MODELS.values()).index(st.session_state.model_name) \
            if st.session_state.model_name in GROQ_MODELS.values() else 0
        
        selected_model = st.selectbox(
            "Choose Groq Model",
            options=model_display_names,
            index=current_model_index,
            help="Groq offers lightning-fast inference"
        )
        
        # Update model if changed
        if GROQ_MODELS[selected_model] != st.session_state.model_name:
            st.session_state.model_name = GROQ_MODELS[selected_model]
            st.session_state.agent = GroqFitnessAgent(
                user_id=st.session_state.user_id,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name=st.session_state.model_name
            )
            st.success(f"Switched to {selected_model}!")
        
        # Speed indicator
        st.markdown("""
        <div class="speed-indicator">
            ⚡ Groq Speed: ~100 tokens/second
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User Profile Section
        st.subheader("👤 Your Fitness Profile")
        
        with st.expander("🎯 Set Your Goals", expanded=True):
            goals = st.text_area(
                "What are your fitness goals?",
                placeholder="e.g., Lose 10kg, build muscle, run a 5K...",
                key="goals_input"
            )
            
            fitness_level = st.select_slider(
                "Fitness Level",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Beginner"
            )
            
            limitations = st.text_area(
                "Any injuries or limitations?",
                placeholder="e.g., Lower back pain, knee issues...",
                key="limitations_input"
            )
            
            equipment = st.multiselect(
                "Available Equipment",
                ["None/Bodyweight", "Dumbbells", "Barbell", "Resistance Bands", 
                 "Kettlebell", "Pull-up Bar", "Treadmill", "Exercise Bike"],
                default=["None/Bodyweight"]
            )
            
            if st.button("💾 Save Profile", use_container_width=True):
                st.session_state.agent.save_user_info(
                    goals=goals,
                    limitations=limitations,
                    equipment=", ".join(equipment),
                    fitness_level=fitness_level.lower()
                )
                st.success("Profile saved! ✅")
                st.balloons()
        
        with st.expander("💪 Quick Workout Log"):
            workout_type = st.selectbox(
                "Workout Type",
                ["Strength Training", "Cardio", "HIIT", "Flexibility", "Other"]
            )
            
            duration = st.number_input("Duration (minutes)", 0, 180, 30)
            
            notes = st.text_area(
                "Workout Details",
                placeholder="e.g., Bench press 3x10 @ 60kg, 20 min treadmill..."
            )
            
            if st.button("📝 Log Workout", use_container_width=True):
                workout_data = {
                    "type": workout_type,
                    "duration": duration,
                    "notes": notes,
                    "difficulty": "moderate"
                }
                st.session_state.agent.log_completed_workout(workout_data)
                st.success("Workout logged! Great job! 🎉")
        
        st.markdown("---")
        
        # Session stats
        st.subheader("📊 Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages", len(st.session_state.messages))
        with col2:
            session_duration = time.time() - st.session_state.start_time
            st.metric("Duration", f"{session_duration:.0f}s")
        
        st.markdown("---")
        
        # Actions
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent.clear_conversation()
            st.rerun()
        
        if st.button("🆕 New Session", use_container_width=True):
            import uuid
            st.session_state.user_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.agent = GroqFitnessAgent(
                user_id=st.session_state.user_id,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name=st.session_state.model_name
            )
            st.rerun()

# Main chat interface
def render_chat():
    st.title("💪 AI Fitness Coach")
    st.caption("Powered by Groq ⚡ | Ultra-fast AI responses")
    
    # Quick suggestion chips
    suggestions = [
        "Create a workout plan for weight loss",
        "How to improve my bench press?",
        "Suggest a healthy meal plan",
        "How to recover from muscle soreness?",
        "Create a HIIT workout"
    ]
    
    # Display suggestions if no messages yet
    if not st.session_state.messages:
        st.markdown("### Get Started! Try asking:")
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": suggestion
                    })
                    st.rerun()
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Add timing for assistant messages
            if message["role"] == "assistant" and "response_time" in message:
                st.caption(f"⚡ Response time: {message['response_time']:.2f}s")
    
    # Chat input
    if prompt := st.chat_input("Ask your AI fitness coach anything..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            start_time = time.time()
            
            try:
                # Get response from agent
                result = st.session_state.agent.chat(prompt)
                response = result['output']
                
                # Calculate response time
                response_time = time.time() - start_time
                
                # Display response
                message_placeholder.markdown(response)
                st.caption(f"⚡ Response time: {response_time:.2f}s")
                
                # Add to messages with timing
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "response_time": response_time
                })
                
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Main app
def main():
    # Load CSS
    load_css()
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        st.warning("⚠️ Please set your GROQ_API_KEY in .env file")
        st.info("Get your free API key at https://console.groq.com")
        
        api_key = st.text_input("Enter your Groq API Key:", type="password")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("API key set! Restarting...")
            st.rerun()
        return
    
    # Initialize session
    init_session()
    
    # Render UI
    render_sidebar()
    render_chat()

if __name__ == "__main__":
    main()
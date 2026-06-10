# src/agent/fitness_agent.py
"""
Fitness Agent powered by Groq + LangChain
Uses direct ChatGroq invocation with ChromaDB context enrichment (RAG pattern).
"""
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from typing import Optional, Dict, List, Any
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.memory.chroma_store import FitnessMemoryStore
from config.settings import GROQ_MODEL, TEMPERATURE, MAX_TOKENS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqFitnessAgent:
    """Production fitness agent using Groq + LangChain with RAG context enrichment"""

    def __init__(
        self,
        user_id: str,
        groq_api_key: str,
        model_name: str = GROQ_MODEL,
        temperature: float = TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
    ):
        self.user_id = user_id

        # Initialize Groq LLM
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Initialize persistent memory store
        self.memory_store = FitnessMemoryStore(user_id=user_id)

        # In-memory conversation history for current session
        self.chat_history: List[BaseMessage] = []

        # System prompt
        self.system_prompt = self._create_system_prompt()

        logger.info(f"Agent initialized with model: {model_name}")

    # ------------------------------------------------------------------
    # System prompt
    # ------------------------------------------------------------------

    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt for fitness agent"""
        return """You are an elite AI fitness coach with deep expertise in:

🏋️ **Strength Training**: Exercise selection, progressive overload, form optimization
🏃 **Cardio & Conditioning**: HIIT, endurance training, heart rate zones
🥗 **Nutrition Science**: Macro/micronutrients, meal timing, dietary patterns
📊 **Progress Tracking**: Metrics, plateaus, adaptation strategies
🧘 **Recovery & Mobility**: Stretching, foam rolling, injury prevention
🎯 **Goal Setting**: SMART goals, periodization, lifestyle integration

Your coaching philosophy:
1. **Safety First**: Always prioritize proper form and injury prevention
2. **Evidence-Based**: Recommendations backed by exercise science
3. **Personalized**: Tailor advice to individual goals, limitations, and preferences
4. **Progressive**: Gradually increase difficulty for continuous improvement
5. **Holistic**: Consider sleep, stress, nutrition, and recovery
6. **Motivational**: Encourage consistency while being realistic

When responding:
- Ask clarifying questions if information is missing
- Provide specific, actionable recommendations
- Include sets, reps, rest periods for exercises
- Explain the "why" behind recommendations
- Use the user profile and context provided to personalize advice
- Suggest modifications for injuries or limitations
- Celebrate progress and milestones

Never recommend dangerous exercises or extreme diets.
Always suggest consulting healthcare providers for medical issues."""

    # ------------------------------------------------------------------
    # Core chat
    # ------------------------------------------------------------------

    def chat(self, message: str) -> Dict[str, Any]:
        """Process a user message and return a response dict with key 'output'."""
        try:
            # 1. Gather context from persistent memory
            context = self.memory_store.get_relevant_context(message)
            profile = self.memory_store.get_user_profile_summary()

            # 2. Build an enriched user message
            enriched_parts = []
            if profile and profile != "New user - no profile yet":
                enriched_parts.append(f"[User Profile]\n{profile}")
            if context:
                enriched_parts.append(f"[Relevant Context]\n{context}")
            enriched_parts.append(f"[Current Message]\n{message}")

            enriched_input = "\n\n".join(enriched_parts)

            # 3. Build the messages list
            messages: List[BaseMessage] = [
                SystemMessage(content=self.system_prompt),
                *self.chat_history[-20:],  # keep last 20 msgs max
                HumanMessage(content=enriched_input),
            ]

            # 4. Invoke the LLM
            response = self.llm.invoke(messages)
            response_text = response.content

            # 5. Update session history (store the *original* message, not the enriched one)
            self.chat_history.append(HumanMessage(content=message))
            self.chat_history.append(AIMessage(content=response_text))

            # 6. Persist to ChromaDB
            self.memory_store.add_conversation(message, response_text)

            return {"output": response_text}

        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return self._fallback_response(message)

    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Last-resort direct LLM call without any context enrichment."""
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=message),
            ]
            response = self.llm.invoke(messages)
            self.memory_store.add_conversation(message, response.content)
            return {"output": response.content}
        except Exception as e:
            return {
                "output": f"I apologize, but I encountered an error: {str(e)}"
            }

    # ------------------------------------------------------------------
    # Profile & workout helpers (called from the Streamlit UI)
    # ------------------------------------------------------------------

    def save_user_info(
        self,
        goals: Optional[str] = None,
        limitations: Optional[str] = None,
        equipment: Optional[str] = None,
        fitness_level: Optional[str] = None,
    ):
        """Save user profile information to persistent memory."""
        if goals:
            self.memory_store.add_preference("goal", goals, "high")
        if limitations:
            self.memory_store.add_preference("limitation", limitations, "high")
        if equipment:
            self.memory_store.add_preference("equipment", equipment, "medium")
        if fitness_level:
            self.memory_store.add_preference("fitness_level", fitness_level, "high")
        logger.info(f"Updated profile for user {self.user_id}")

    def log_completed_workout(self, workout_data: Dict):
        """Log a completed workout to persistent memory."""
        self.memory_store.add_workout(workout_data)
        logger.info(f"Workout logged for user {self.user_id}")

    def get_conversation_history(self, n: int = 10) -> List[Dict]:
        """Get recent conversations for display."""
        return self.memory_store.get_recent_conversations(n)

    def clear_conversation(self):
        """Clear the current session's in-memory chat history."""
        self.chat_history = []
        logger.info(f"Conversation cleared for user {self.user_id}")
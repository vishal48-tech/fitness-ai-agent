# src/agent/fitness_agent.py
"""
Fitness Agent V2 powered by Groq + LangChain.
Supports multi-user authentication with profile context fetched from Supabase.
Integrates ChromaDB Cloud for per-user semantic memory retrieval (RAG).
Includes streaming responses for interactive UI output.
"""
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from typing import Optional, Dict, List, Any, Iterator
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
    """Fitness Agent using Groq + ChromaDB Cloud with Supabase user profile context."""

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

        # Initialize ChromaDB Cloud memory store
        self.memory_store = FitnessMemoryStore(user_id=user_id)

        # System prompt
        self.system_prompt = self._create_system_prompt()

        logger.info(f"Agent V2 initialized with model: {model_name} for user: {user_id}")

    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt for the fitness agent."""
        return """You are an elite AI fitness coach with deep expertise in:

🏋️ **Strength Training**: Exercise selection, progressive overload, form optimization
🏃 **Cardio & Conditioning**: HIIT, endurance training, heart rate zones
🥗 **Nutrition Science**: Macro/micronutrients, meal timing, dietary patterns
📊 **Progress Tracking**: Metrics, plateaus, adaptation strategies
🧘 **Recovery & Mobility**: Stretching, foam rolling, injury prevention
🎯 **Goal Setting**: SMART goals, periodization, lifestyle integration

Your coaching philosophy:
1. **Safety First**: Always prioritize proper form and injury prevention.
2. **Evidence-Based**: Recommendations backed by exercise science.
3. **Personalized**: Tailor advice to individual goals, limitations, and preferences.
4. **Progressive**: Gradually increase difficulty for continuous improvement.
5. **Holistic**: Consider sleep, stress, nutrition, and recovery.
6. **Motivational**: Encourage consistency while being realistic.

When responding:
- Ask clarifying questions if information is missing.
- Provide specific, actionable recommendations.
- Include sets, reps, rest periods for exercises.
- Explain the "why" behind recommendations.
- Use the user profile and context provided to personalize advice.
- Suggest modifications for injuries or limitations.
- Celebrate progress and milestones.

Never recommend dangerous exercises or extreme diets.
Always suggest consulting healthcare providers for medical issues."""

    def chat_stream(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Iterator[str]:
        """Process a user message and return a generator yielding response chunks.

        Enriches the message with profile database context and Chroma Cloud semantic history.
        """
        # 1. Gather context from Chroma Cloud (semantic search)
        semantic_context = self.memory_store.get_relevant_context(message)

        # 2. Extract profile details
        profile_parts = []
        if user_profile:
            profile_parts.append(f"Name: {user_profile.get('display_name', 'User')}")
            profile_parts.append(f"Goals: {user_profile.get('goals', 'Not specified')}")
            profile_parts.append(f"Limitations: {user_profile.get('limitations', 'None')}")
            profile_parts.append(f"Equipment: {user_profile.get('equipment', 'None/Bodyweight')}")
            profile_parts.append(f"Fitness Level: {user_profile.get('fitness_level', 'Beginner')}")
        profile_context = "\n".join(profile_parts)

        # 3. Build enriched input
        enriched_parts = []
        if profile_context:
            enriched_parts.append(f"[User Profile]\n{profile_context}")
        if semantic_context:
            enriched_parts.append(f"[Relevant Historical Context]\n{semantic_context}")
        enriched_parts.append(f"[Current User Message]\n{message}")

        enriched_input = "\n\n".join(enriched_parts)

        # 4. Construct message history list
        messages: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]
        
        # Add past session messages
        for msg in chat_history[-20:]:  # Limit to 20 messages for context window
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # Add the new message with the loaded context
        messages.append(HumanMessage(content=enriched_input))

        # 5. Stream the response from the LLM
        response_text_accumulator = []
        try:
            for chunk in self.llm.stream(messages):
                content = chunk.content
                if content:
                    response_text_accumulator.append(content)
                    yield content

            # 6. Save full exchange to Chroma Cloud in the background
            full_response = "".join(response_text_accumulator)
            self.memory_store.add_conversation(message, full_response)
        except Exception as e:
            logger.error(f"Error in chat_stream: {e}", exc_info=True)
            yield f"I apologize, but I encountered an error: {str(e)}"
# src/memory/chroma_store.py
"""
Production-ready ChromaDB memory store.
Uses ChromaDB's built-in default embedding function (all-MiniLM-L6-v2 via onnxruntime)
so there is no dependency on langchain memory classes or HuggingFace wrappers.
"""
import chromadb
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FitnessMemoryStore:
    """Advanced memory management for fitness agent using ChromaDB"""

    def __init__(
        self,
        persist_directory: str = "./chroma_data",
        user_id: str = "default",
    ):
        self.user_id = user_id
        self.persist_directory = persist_directory

        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Initialize collections (uses ChromaDB default embedding function)
        self._init_collections()

    # ------------------------------------------------------------------
    # Collection management
    # ------------------------------------------------------------------

    def _init_collections(self):
        """Initialize all ChromaDB collections"""
        self.conversations = self.client.get_or_create_collection(
            name=f"conversations_{self.user_id}",
        )
        self.preferences = self.client.get_or_create_collection(
            name=f"preferences_{self.user_id}",
        )
        self.workouts = self.client.get_or_create_collection(
            name=f"workouts_{self.user_id}",
        )
        self.knowledge_base = self.client.get_or_create_collection(
            name=f"knowledge_base_{self.user_id}",
        )
        self.progress = self.client.get_or_create_collection(
            name=f"progress_{self.user_id}",
        )

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def add_conversation(
        self, user_message: str, ai_response: str, metadata: Dict = None
    ):
        """Store a conversation exchange"""
        conversation_text = f"User: {user_message}\nAssistant: {ai_response}"

        base_metadata = {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "type": "conversation",
            "message_length": len(user_message),
            "response_length": len(ai_response),
        }
        if metadata:
            base_metadata.update(metadata)

        self.conversations.add(
            documents=[conversation_text],
            metadatas=[base_metadata],
            ids=[f"conv_{uuid.uuid4()}"],
        )

    def add_preference(
        self,
        preference_type: str,
        content: str,
        importance: str = "medium",
    ):
        """Store user preferences"""
        self.preferences.add(
            documents=[content],
            metadatas=[
                {
                    "user_id": self.user_id,
                    "preference_type": preference_type,
                    "importance": importance,
                    "timestamp": datetime.now().isoformat(),
                }
            ],
            ids=[f"pref_{uuid.uuid4()}"],
        )

        # High-importance items are also stored in conversations for retrieval
        if importance == "high":
            summary = f"IMPORTANT: {preference_type} - {content}"
            self.conversations.add(
                documents=[summary],
                metadatas=[
                    {
                        "user_id": self.user_id,
                        "type": "important_preference",
                        "preference_type": preference_type,
                        "timestamp": datetime.now().isoformat(),
                    }
                ],
                ids=[f"important_{uuid.uuid4()}"],
            )

    def add_workout(self, workout_data: Dict):
        """Log a completed workout"""
        workout_text = self._format_workout(workout_data)

        self.workouts.add(
            documents=[workout_text],
            metadatas=[
                {
                    "user_id": self.user_id,
                    "workout_type": str(workout_data.get("type", "general")),
                    "duration": int(workout_data.get("duration", 0)),
                    "difficulty": str(workout_data.get("difficulty", "moderate")),
                    "timestamp": datetime.now().isoformat(),
                }
            ],
            ids=[f"workout_{uuid.uuid4()}"],
        )

    def add_knowledge(self, topic: str, content: str, source: str = "general"):
        """Add to fitness knowledge base"""
        self.knowledge_base.add(
            documents=[content],
            metadatas=[
                {
                    "topic": topic,
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                }
            ],
            ids=[f"kb_{uuid.uuid4()}"],
        )

    # ------------------------------------------------------------------
    # Read / query helpers
    # ------------------------------------------------------------------

    def _safe_query(self, collection, query: str, n_results: int = 5):
        """Query a collection, gracefully handling empty collections."""
        try:
            count = collection.count()
            if count == 0:
                return {"documents": [[]], "distances": [[]], "metadatas": [[]]}
            return collection.query(
                query_texts=[query],
                n_results=min(n_results, count),
            )
        except Exception as exc:
            logger.debug(f"Query failed on {collection.name}: {exc}")
            return {"documents": [[]], "distances": [[]], "metadatas": [[]]}

    def get_relevant_context(self, query: str, n_results: int = 5) -> str:
        """Retrieve relevant context from all memory stores"""
        context_parts: List[str] = []

        # Conversations
        conv_results = self._safe_query(self.conversations, query, n_results)
        if conv_results["documents"][0]:
            context_parts.append("📝 Related Conversations:")
            for i, doc in enumerate(conv_results["documents"][0]):
                dist = (
                    conv_results["distances"][0][i]
                    if conv_results["distances"][0]
                    else 1.0
                )
                if (1 - dist) > 0.3:
                    context_parts.append(f"  • {doc[:200]}...")

        # Preferences
        pref_results = self._safe_query(self.preferences, query, 3)
        if pref_results["documents"][0]:
            context_parts.append("\n🎯 Your Preferences & Goals:")
            for doc in pref_results["documents"][0]:
                context_parts.append(f"  • {doc}")

        # Workouts
        workout_results = self._safe_query(self.workouts, query, 3)
        if workout_results["documents"][0]:
            context_parts.append("\n💪 Recent Workouts:")
            for i, doc in enumerate(workout_results["documents"][0]):
                dist = (
                    workout_results["distances"][0][i]
                    if workout_results["distances"][0]
                    else 1.0
                )
                if (1 - dist) > 0.3:
                    context_parts.append(f"  • {doc[:150]}...")

        return "\n".join(context_parts) if context_parts else ""

    def get_user_profile_summary(self) -> str:
        """Generate a comprehensive user-profile string"""
        profile_parts: List[str] = []

        # Preferences
        try:
            prefs = self.preferences.get()
            if prefs["documents"]:
                profile_parts.append("## User Profile")
                for doc, meta in zip(prefs["documents"], prefs["metadatas"]):
                    ptype = meta.get("preference_type", "general")
                    profile_parts.append(f"- [{ptype}] {doc}")
        except Exception:
            pass

        # Workout stats
        try:
            workouts = self.workouts.get()
            if workouts["ids"]:
                total = len(workouts["ids"])
                profile_parts.append(f"\n## Workout Stats")
                profile_parts.append(f"- Total workouts logged: {total}")
                durations = [
                    m["duration"]
                    for m in workouts["metadatas"]
                    if "duration" in m and m["duration"]
                ]
                if durations:
                    avg = sum(durations) / len(durations)
                    profile_parts.append(
                        f"- Average workout duration: {avg:.0f} minutes"
                    )
        except Exception:
            pass

        # Progress
        try:
            prog = self.progress.get()
            if prog["ids"]:
                profile_parts.append(f"\n## Progress Tracking")
                profile_parts.append(f"- Progress entries: {len(prog['ids'])}")
        except Exception:
            pass

        return "\n".join(profile_parts) if profile_parts else "New user - no profile yet"

    def search_knowledge_base(self, query: str, n_results: int = 3) -> str:
        """Search the fitness knowledge base"""
        results = self._safe_query(self.knowledge_base, query, n_results)
        if results["documents"][0]:
            return "\n\n".join(results["documents"][0])
        return "No specific knowledge found for this topic."

    def get_workout_history(self) -> str:
        """Return recent workout history as a formatted string"""
        try:
            workouts = self.workouts.get()
            if workouts["ids"]:
                recent = list(zip(workouts["documents"], workouts["metadatas"]))
                recent.sort(
                    key=lambda x: x[1].get("timestamp", ""), reverse=True
                )
                return "\n\n".join([doc for doc, _ in recent[:5]])
        except Exception:
            pass
        return "No workout history yet"

    def get_recent_conversations(self, n: int = 5) -> List[Dict]:
        """Get recent conversations for display"""
        try:
            results = self.conversations.get()
            if results["ids"]:
                convs = list(
                    zip(results["ids"], results["documents"], results["metadatas"])
                )
                convs = [
                    c for c in convs if c[2].get("type") != "important_preference"
                ]
                convs.sort(
                    key=lambda x: x[2].get("timestamp", ""), reverse=True
                )
                return [
                    {"id": c[0], "content": c[1], "metadata": c[2]}
                    for c in convs[:n]
                ]
        except Exception:
            pass
        return []

    def clear_session(self):
        """Lightweight reset (does NOT delete persistent data)"""
        pass  # reserved for future session-buffer logic

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_workout(workout_data: Dict) -> str:
        parts = [f"Workout: {workout_data.get('type', 'General Workout')}"]
        parts.append(f"Duration: {workout_data.get('duration', 'N/A')} minutes")
        parts.append(f"Difficulty: {workout_data.get('difficulty', 'moderate')}")

        if "exercises" in workout_data:
            parts.append("Exercises:")
            for ex in workout_data["exercises"]:
                parts.append(
                    f"- {ex.get('name')}: "
                    f"{ex.get('sets')}x{ex.get('reps')} "
                    f"@ {ex.get('weight', 'bodyweight')}"
                )

        if "notes" in workout_data:
            parts.append(f"Notes: {workout_data['notes']}")

        return "\n".join(parts)
# src/llm/model_manager.py
"""
Simplified LLM manager using Ollama
"""
import requests
import subprocess
import sys
from typing import Generator, Optional

class OllamaLLM:
    """Simple wrapper around Ollama for LLM interactions"""
    
    def __init__(self, model_name: str = "mistral:7b-instruct-v0.2-q4_K_M", 
                 base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        
        # Check if Ollama is running
        self._check_ollama()
        # Ensure model is available
        self._ensure_model()
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                print("⚠️  Ollama is not running! Start it with: ollama serve")
                print("Then install it from: https://ollama.ai")
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama!")
            print("Make sure Ollama is installed and running:")
            print("1. Install: curl -fsSL https://ollama.ai/install.sh | sh")
            print("2. Run: ollama serve")
            sys.exit(1)
    
    def _ensure_model(self):
        """Download model if not available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            models = [m['name'] for m in response.json().get('models', [])]
            
            if self.model_name not in models:
                print(f"📥 Downloading model {self.model_name}...")
                print("This may take a few minutes...")
                subprocess.run(["ollama", "pull", self.model_name], check=True)
                print(f"✅ Model {self.model_name} ready!")
        except Exception as e:
            print(f"Error checking model: {e}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response (non-streaming)"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "system": system_prompt or self._default_system_prompt(),
                    "stream": False
                }
            )
            return response.json()['response']
        except Exception as e:
            return f"Error generating response: {e}"
    
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate a streaming response"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "system": system_prompt or self._default_system_prompt(),
                    "stream": True
                },
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    import json
                    chunk = json.loads(line)
                    if 'response' in chunk:
                        yield chunk['response']
        except Exception as e:
            yield f"Error: {e}"
    
    def _default_system_prompt(self) -> str:
        """Default fitness coach system prompt"""
        return """You are an expert AI fitness coach. You provide:
- Personalized workout advice
- Exercise form guidance
- Nutrition recommendations
- Motivation and support

Always prioritize safety and proper form. Be encouraging but honest."""
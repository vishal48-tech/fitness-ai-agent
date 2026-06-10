# AI Fitness Coach

An intelligent fitness assistant powered by Groq AI with persistent memory using ChromaDB.

---

## 🚧 Current Status

**V1 is live and functional** (what you can use today)  
**V2 is planned** (features to be implemented)

---

## ✅ V1 Features (Current Release)

| Feature | Status |
|---------|--------|
| 💬 Conversational AI fitness coach | ✅ Live |
| 🧠 Persistent memory (remembers preferences) | ✅ Live |
| 📊 Workout logging and tracking | ✅ Live |
| 🎯 Personalized recommendations | ✅ Live |
| ⚡ Lightning-fast responses via Groq | ✅ Live |

---

## 🔜 V2 Features (Roadmap)

> These improvements are planned for the next release.

| Feature | Description |
|---------|-------------|
| 🔐 User Authentication | Login and signup system so chats/workouts load per session |
| 📊 User Dashboard | Central hub for recent chats, saved plans, quick actions |
| ⌨️ Streaming Responses (`iter`) | Text generates word‑by‑word (typewriter effect) instead of appearing all at once |
| 🎛️ Dropdown Workout Generator | Predefined dropdowns + "Generate Workout" button → no manual prompt writing |

### V2 Details

#### 1. User Authentication (Login & Signup)
- Each user has their own chat history
- Past conversations load automatically after login
- Workouts saved per user account

#### 2. User Dashboard
- Personalized landing page after login
- Shows recent chats and saved workouts
- Quick action buttons: *New Chat*, *Generate Workout*, *View History*

#### 3. Streaming Text Generation (`iter`)
- Responses appear token‑by‑token (live typing effect)
- Better user experience than waiting for full response

#### 4. Dropdown‑Based Workout Generator

Planned dropdowns:

1. Primary Goal
2. Experience Level
3. Available Time Per Session
4. Available Equipment
5. Training Frequency (Days Per Week)
6. Training Style Preference
7. Focus Areas
8. Special Considerations
9. Preferred Training Vibe
10. Age
11. Height
12. Weight

> **Generate Workout** button will compile selections into a prompt automatically.

---

## 📦 Quick Start (V1 – Current Version)

### Local Development

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd fitness-ai-agent

# 2. Create virtual environment
uv venv .venv

# 3. Activate (Windows)
.venv\Scripts\activate
# Or (Linux/Mac)
source .venv/bin/activate

# 4. Install dependencies
uv pip install -r requirements.txt

# 5. Create .env file with your GROQ_API_KEY
echo "GROQ_API_KEY=your_key_here" > .env

# 6. Run the app
streamlit run app.py
```

### Docker Deployment

```bash
docker build -t ai-fitness-coach .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key ai-fitness-coach
```

---


## 🛠️ Tech Stack (V1)

| Component | Technology |
|-----------|-------------|
| Frontend/UI | Streamlit |
| AI Inference | Groq API |
| Memory | ChromaDB |
| Language | Python |

---

## 📝 Changelog

### V1 (Current)
- Initial release
- Conversational fitness coach
- ChromaDB memory persistence

### V2 (Planned)
- User authentication
- Dashboard
- Streaming responses
- Dropdown workout generator

---

## 📄 License

MIT

---

## 🙌 Acknowledgments

- [Groq](https://groq.com) – Lightning-fast inference
- [ChromaDB](https://www.trychroma.com) – Persistent vector memory
- [Streamlit](https://streamlit.io) – Rapid UI development for V1
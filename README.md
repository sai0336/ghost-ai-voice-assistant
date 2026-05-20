# 👻 GHOST — AI Voice Assistant

> *"Listening, Sir. Say 'Ghost' to activate."*

A tactical AI voice assistant inspired by **Ghost from Call of Duty**, built with Python. Features multi-provider AI fallback, voice recognition, camera vision, and full PC control — all hands-free.

---

## ⚡ Features

| Feature | Details |
|---|---|
| 🎙️ Wake Word | Say **"Ghost"** to activate |
| 🤖 Multi-AI Fallback | Auto-switches between 6 AI providers (Groq → Cerebras → SambaNova → OpenRouter → Cohere → Mistral) |
| 👁️ Camera Vision | Identify objects, read text, detect emotions via Gemini |
| 🌐 Web Search | Search Google, open websites, play YouTube |
| 🌤️ Weather | Real-time weather for any city |
| 📰 News | Latest headlines via NewsAPI |
| 🖥️ PC Control | Volume, screenshot, shutdown, restart, lock screen |
| 📱 App Launcher | Open VS Code, Chrome, Notepad, Calculator |
| ⏰ Reminders | Set voice reminders |
| 🌍 Multi-Language | English, Hindi, Marathi |
| 🔐 Password Gen | Generate strong passwords by voice |
| 📡 Speed Test | Check internet speed by voice |

---

## 🤖 AI Provider Chain

Ghost auto-rotates through free AI providers on quota/failure:

| Priority | Provider | Free Limit | Speed |
|---|---|---|---|
| 1 | **Groq** | 14,400 req/day | ⚡ Instant |
| 2 | **Cerebras** | ~Unlimited | ⚡ Very Fast |
| 3 | **SambaNova** | ~Unlimited | ⚡ Fast |
| 4 | **OpenRouter** | Free models | ✅ Good |
| 5 | **Cohere** | 1000/month | ✅ Good |
| 6 | **Mistral** | Limited free | ✅ Good |
| Vision | **Gemini** | 1500/day | Camera only |

---

## 🚀 Setup & Installation

### Step 1 — Clone the repo
```bash
git clone https://github.com/saichavan/ghost-ai-voice-assistant
cd ghost-ai-voice-assistant
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Set up API keys
```bash
# Copy the template
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux

# Open .env and fill in your API keys
notepad .env
```

### Step 4 — Run Ghost
```bash
python ghost.py
```

---

## 🔑 Getting Free API Keys

| Key | Where to Get |
|---|---|
| `GROQ_API_KEY` | console.groq.com → API Keys |
| `CEREBRAS_API_KEY` | inference.cerebras.ai → API Keys |
| `SAMBANOVA_API_KEY` | cloud.sambanova.ai → API Key |
| `OPENROUTER_API_KEY` | openrouter.ai → Keys |
| `COHERE_API_KEY` | dashboard.cohere.com → API Keys |
| `GEMINI_API_KEY_1` | aistudio.google.com |
| `WEATHER_API_KEY` | openweathermap.org |
| `YOUTUBE_API_KEY` | console.cloud.google.com |
| `NEWS_API_KEY` | newsapi.org |

---

## 🗣️ Voice Commands

```
"Ghost, what's the weather in Mumbai"
"Ghost, play Believer on YouTube"
"Ghost, search quantum computing"
"Ghost, take a screenshot"
"Ghost, what do you see"       ← opens camera
"Ghost, volume up"
"Ghost, set a reminder in 10 minutes"
"Ghost, what's the news today"
"Ghost, run speed test"
"Ghost, generate a password"
"Ghost, open VS Code"
"Ghost, shutdown system"
```

---

## 📁 File Structure

```
ghost-ai-voice-assistant/
│
├── ghost.py              # Main assistant code
├── .env.example          # API keys template (copy → rename to .env)
├── .gitignore            # Keeps your .env safe
├── requirements.txt      # All dependencies
└── README.md
```

---

## ⚠️ Requirements

- Windows 10/11 (uses Windows audio & system APIs)
- Python 3.9+
- Microphone
- Webcam (optional, for vision features)
- Internet connection

---

## 👨‍💻 Made By

**Sai Santosh Chavan**
B.Sc. IT Student | Mumbai


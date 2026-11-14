# Ghost — AI Voice Assistant

A voice assistant built in Python, named after Ghost from Call of Duty. Say "Ghost" to activate it.

Built this to experiment with free AI APIs and see how many useful things a voice assistant could actually do without paying for anything.

---

## How it works

Ghost listens for the wake word "Ghost" using the microphone. Once activated, it records your voice, converts it to text using speech recognition, sends it to an AI provider, and speaks the response back using text-to-speech.

The code attempts provider/model fallbacks when requests fail or hit limits. Availability depends on current API access, provider quotas, and compatible model IDs.

---

## AI Provider Chain

Ghost cycles through these providers in order:

| Priority | Provider | Notes |
|---|---|---|
| 1 | Groq | Fast, generous free tier |
| 2 | Cerebras | Very fast inference |
| 3 | SambaNova | Reliable fallback |
| 4 | OpenRouter | Access to multiple models |
| 5 | Cohere | Additional fallback |
| 6 | Mistral | Final fallback |
| Vision only | Gemini | Used for camera features |

---

## Features

- Wake word activation — say "Ghost" to trigger
- Multi-provider AI with automatic fallback
- Weather for any city
- Latest news headlines
- YouTube search and play
- Google search
- Camera vision — identify objects, read text, detect faces
- Volume control
- Screenshot
- Open apps like VS Code, Chrome, Notepad
- Set reminders by voice
- Generate passwords by voice
- Internet speed test
- PC shutdown, restart, lock

---

## Requirements

- Windows 10 or 11
- Python 3.9 or higher
- Microphone
- Webcam (optional, for camera features)
- Internet connection

---

## Setup

### Step 1 — Clone the repo

```
git clone https://github.com/sai0336/ghost-ai-voice-assistant
cd ghost-ai-voice-assistant
```

### Step 2 — Install dependencies

```
pip install -r requirements.txt
```

### Step 3 — Set up API keys

On Windows Command Prompt:

```bat
copy .env.example .env
```

Use only keys issued to you; never commit `.env`.

Open the `.env` file and fill in your API keys. See the table below for where to get each one.

### Step 4 — Run

```
python ghost.py
```

---

## Getting API keys

Check each provider's current pricing and free-tier availability; limits and supported models can change:

| Key | Where to get it |
|---|---|
| GROQ_API_KEY | console.groq.com |
| CEREBRAS_API_KEY | inference.cerebras.ai |
| SAMBANOVA_API_KEY | cloud.sambanova.ai |
| OPENROUTER_API_KEY | openrouter.ai |
| COHERE_API_KEY | dashboard.cohere.com |
| MISTRAL_API_KEY | console.mistral.ai |
| GEMINI_API_KEY | aistudio.google.com |
| WEATHER_API_KEY | openweathermap.org |
| YOUTUBE_API_KEY | console.cloud.google.com |
| NEWS_API_KEY | newsapi.org |

---

## Voice commands

```
Ghost, what's the weather in Mumbai
Ghost, play Believer on YouTube
Ghost, search quantum computing
Ghost, take a screenshot
Ghost, what do you see
Ghost, volume up
Ghost, set a reminder in 10 minutes
Ghost, what's the news today
Ghost, run speed test
Ghost, generate a password
Ghost, open VS Code
Ghost, shutdown
```

---

## File structure

```
ghost-ai-voice-assistant/
|
|-- ghost.py
|-- .env.example
|-- .gitignore
|-- requirements.txt
|-- README.md
```

---

## Note

Never upload your `.env` file to GitHub. It contains your API keys. The `.gitignore` excludes local `.env` files. Do not commit real credentials. If credentials were committed previously, revoke and replace them; adding `.gitignore` does not erase Git history.

---

Built by [Sai Chavan](https://github.com/sai0336)

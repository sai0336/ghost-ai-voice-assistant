# ============================================================
#  G H O S T  —  Voice Assistant
#  Inspired by Ghost from Call of Duty | Created by Sai
#
#  AI PROVIDER CHAIN (auto-rotates on quota/failure):
#  1. Groq         — console.groq.com        — 14,400/day FREE
#  2. Cerebras     — inference.cerebras.ai   — unlimited* FREE
#  3. SambaNova    — cloud.sambanova.ai      — unlimited* FREE
#  4. OpenRouter   — openrouter.ai           — free models FREE
#  5. Cohere       — dashboard.cohere.com    — 1000/month FREE
#  6. Mistral      — console.mistral.ai      — limited FREE
#  7. Gemini       — aistudio.google.com     — vision only
# ============================================================

import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import subprocess
import google.generativeai as genai
import time
import requests
from googleapiclient.discovery import build
import threading
import psutil
import pyautogui
import cv2
from PIL import Image
import random
import re
import speedtest
import string
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import shutil
import edge_tts
import asyncio
import pygame
import io
import queue as _queue
from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file


# ============================================================
#  ★  API KEYS — FILL THESE IN  ★
#  Each provider is FREE. Get all 6 for maximum reliability.
# ============================================================

# 1. GROQ — console.groq.com → API Keys → Create
#    Free: 14,400 req/day | Speed: instant (LPU hardware)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# 2. CEREBRAS — inference.cerebras.ai → API Keys
#    Free: ~unlimited for personal use | Speed: very fast
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")

# 3. SAMBANOVA — cloud.sambanova.ai → API Key
#    Free: ~unlimited for personal use | Speed: fast
SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY", "")

# 4. OPENROUTER — openrouter.ai → Keys (free models available)
#    Free models: meta-llama/llama-3.1-8b-instruct:free etc.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# 5. COHERE — dashboard.cohere.com → API Keys
#    Free: 1000 req/month | Good quality
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")

# 6. MISTRAL — console.mistral.ai → API Keys
#    Free tier available | Good quality
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# 7. GEMINI — aistudio.google.com (used for vision/camera only)
GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY_1", ""),
    # "AIza...",  # add more Gemini keys for vision fallback
]

# Other API keys
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
NEWS_API_KEY    = os.getenv("NEWS_API_KEY", "")


# ============================================================
#  ASSISTANT IDENTITY
# ============================================================
ASSISTANT_NAME = "ghost"
USER_NAME      = "Sir"
USER_CREATOR   = "Sai"

current_language = "en-IN"   # en-IN | hi-IN | mr-IN

APP_PATHS = {
    "code":       f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "notepad":    "C:\\Windows\\System32\\notepad.exe",
    "calculator": "C:\\Windows\\System32\\calc.exe",
    "chrome":     "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
}


# ============================================================
#  AI PROVIDER DEFINITIONS
#  All OpenAI-compatible REST except Cohere and Gemini.
#  Format: name, endpoint, auth_header, model list, request_fn
# ============================================================

# Ghost system prompt — used by all providers
def _ghost_prompt(lang_name: str) -> str:
    return (
        f"You are Ghost, a tactical AI assistant by {USER_CREATOR}, "
        f"inspired by Ghost from Call of Duty. "
        f"Be direct, max 2 sentences, British military tone. "
        f"Call user '{USER_NAME}'. Reply ONLY in {lang_name}. No English if lang is not English."
    )


# ── Provider configs ─────────────────────────────────────────
# Each provider: { endpoint, key, models, style }
# style: "openai" | "cohere"
# "openai" = standard chat/completions format (Groq, Cerebras, SambaNova, OpenRouter, Mistral)
# "cohere"  = Cohere's own format

PROVIDERS = [
    {
        "name":     "Groq",
        "key_var":  "GROQ_API_KEY",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "style":    "openai",
        "models":   ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
    },
    {
        "name":     "Cerebras",
        "key_var":  "CEREBRAS_API_KEY",
        "endpoint": "https://api.cerebras.ai/v1/chat/completions",
        "style":    "openai",
        "models":   ["llama3.1-8b", "llama-3.3-70b"],
    },
    {
        "name":     "SambaNova",
        "key_var":  "SAMBANOVA_API_KEY",
        "endpoint": "https://api.sambanova.ai/v1/chat/completions",
        "style":    "openai",
        "models":   ["Meta-Llama-3.1-8B-Instruct", "Meta-Llama-3.3-70B-Instruct"],
    },
    {
        "name":     "OpenRouter",
        "key_var":  "OPENROUTER_API_KEY",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "style":    "openai",
        "models":   [
            "meta-llama/llama-3.1-8b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "google/gemma-2-9b-it:free",
        ],
        "extra_headers": {"HTTP-Referer": "https://ghost-assistant.local"},
    },
    {
        "name":     "Cohere",
        "key_var":  "COHERE_API_KEY",
        "endpoint": "https://api.cohere.com/v2/chat",
        "style":    "cohere",
        "models":   ["command-r", "command-r-plus"],
    },
    {
        "name":     "Mistral",
        "key_var":  "MISTRAL_API_KEY",
        "endpoint": "https://api.mistral.ai/v1/chat/completions",
        "style":    "openai",
        "models":   ["mistral-small-latest", "open-mistral-7b"],
    },
]

# Cooldown tracker: "ProviderName::model" → reset_timestamp
_provider_limited: dict = {}


def _provider_key(provider: dict) -> str:
    """Get actual API key string for a provider."""
    return globals().get(provider["key_var"], "")


def _key_valid(key: str) -> bool:
    return bool(key) and not key.startswith("PASTE_")


def _is_limited(provider_name: str, model: str) -> bool:
    slot = f"{provider_name}::{model}"
    if slot not in _provider_limited:
        return False
    if time.time() >= _provider_limited[slot]:
        del _provider_limited[slot]
        return False
    return True


def _mark_limited(provider_name: str, model: str, retry_secs: float = 60.0):
    slot = f"{provider_name}::{model}"
    _provider_limited[slot] = time.time() + retry_secs
    print(f"  [{provider_name}/{model}] cooldown {retry_secs:.0f}s")


def _parse_retry(resp_headers: dict, body_text: str) -> float:
    """Extract retry-after seconds from headers or body."""
    ra = resp_headers.get("retry-after", "")
    if ra:
        try:
            return float(ra)
        except Exception:
            pass
    m = re.search(r'retry in (\d+(?:\.\d+)?)s', body_text)
    if m:
        return float(m.group(1))
    m = re.search(r'"seconds":\s*(\d+)', body_text)
    if m:
        return float(m.group(1))
    return 60.0


def _call_openai_style(provider: dict, model: str, messages: list, max_tokens: int) -> str:
    """Call any OpenAI-compatible chat completions endpoint."""
    key = _provider_key(provider)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
    }
    if "extra_headers" in provider:
        headers.update(provider["extra_headers"])

    resp = requests.post(
        provider["endpoint"],
        headers=headers,
        json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7},
        timeout=10,
    )

    if resp.status_code == 429:
        retry = _parse_retry(dict(resp.headers), resp.text)
        _mark_limited(provider["name"], model, retry)
        return ""

    if resp.status_code in (401, 403):
        print(f"  [{provider['name']}] auth error — check key")
        _mark_limited(provider["name"], model, 3600)  # 1hr cooldown for bad key
        return ""

    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _call_cohere_style(provider: dict, model: str, messages: list, max_tokens: int) -> str:
    """Call Cohere v2 chat endpoint."""
    key = _provider_key(provider)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
    }
    # Cohere v2 uses same messages format as OpenAI
    resp = requests.post(
        provider["endpoint"],
        headers=headers,
        json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7},
        timeout=10,
    )

    if resp.status_code == 429:
        retry = _parse_retry(dict(resp.headers), resp.text)
        _mark_limited(provider["name"], model, retry)
        return ""

    if resp.status_code in (401, 403):
        print(f"  [{provider['name']}] auth error")
        _mark_limited(provider["name"], model, 3600)
        return ""

    resp.raise_for_status()
    data = resp.json()
    # Cohere v2 response: data["message"]["content"][0]["text"]
    try:
        return data["message"]["content"][0]["text"].strip()
    except Exception:
        return data.get("text", "").strip()


def call_ai(prompt: str, max_tokens: int = 150) -> str:
    """
    Master AI router — tries every provider + model in order.
    Skips any provider/model still in cooldown.
    Returns first successful response or "" if all fail.

    Chain: Groq → Cerebras → SambaNova → OpenRouter → Cohere → Mistral
    """
    lang_name = LANG_NAMES.get(current_language, "English")
    messages  = [
        {"role": "system", "content": _ghost_prompt(lang_name)},
        {"role": "user",   "content": prompt},
    ]

    for provider in PROVIDERS:
        key = _provider_key(provider)
        if not _key_valid(key):
            continue  # skip unconfigured providers silently

        for model in provider["models"]:
            if _is_limited(provider["name"], model):
                remain = int(_provider_limited[f"{provider['name']}::{model}"] - time.time())
                print(f"  [{provider['name']}/{model}] limited {remain}s — skip")
                continue

            try:
                print(f"  Trying [{provider['name']}/{model}]...")
                if provider["style"] == "cohere":
                    result = _call_cohere_style(provider, model, messages, max_tokens)
                else:
                    result = _call_openai_style(provider, model, messages, max_tokens)

                if result:
                    return result
                # empty string = marked limited or soft fail, try next

            except requests.exceptions.Timeout:
                print(f"  [{provider['name']}/{model}] timeout")
                _mark_limited(provider["name"], model, 30)
                continue
            except requests.exceptions.ConnectionError:
                print(f"  [{provider['name']}/{model}] connection error")
                continue
            except Exception as e:
                print(f"  [{provider['name']}/{model}] error: {e}")
                continue

    # All providers failed
    all_slots = list(_provider_limited.values())
    if all_slots:
        wait = max(0, int(min(all_slots) - time.time()))
        print(f"All AI providers limited. Soonest free in {wait}s.")
    return ""


# ============================================================
#  VOICE CONFIGURATION
# ============================================================
VOICES = {
    "en-IN": {"voice": "en-US-ChristopherNeural", "rate": "+25%", "pitch": "-8Hz"},
    "hi-IN": {"voice": "hi-IN-MadhurNeural",       "rate": "+20%", "pitch": "-5Hz"},
    "mr-IN": {"voice": "mr-IN-ManoharNeural",      "rate": "+20%", "pitch": "-5Hz"},
}

LANG_NAMES       = {"en-IN": "English", "hi-IN": "Hindi", "mr-IN": "Marathi"}
RECOGNITION_LANG = {"en-IN": "en-IN",   "hi-IN": "hi-IN", "mr-IN": "mr-IN"}

# ── Pygame ───────────────────────────────────────────────────
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.init()

# ── Single asyncio loop for TTS ──────────────────────────────
_loop = asyncio.new_event_loop()
threading.Thread(target=_loop.run_forever, daemon=True, name="TTSLoop").start()

# ── State ────────────────────────────────────────────────────
CACHE                = {}
CACHE_EXPIRY_SECONDS = 600
stop_assistant       = threading.Event()
is_speaking          = threading.Event()
tts_lock             = threading.Lock()
_command_lock        = threading.Lock()

# ── Audio cache ──────────────────────────────────────────────
_audio_cache: dict = {}

QUICK_PHRASES = {
    "ack":      "Yeah.",
    "thinking": "On it.",
    "error":    "Something went wrong.",
}

# ── Shared recognizer ────────────────────────────────────────
_recognizer = sr.Recognizer()
_recognizer.pause_threshold          = 0.6
_recognizer.energy_threshold         = 300
_recognizer.dynamic_energy_threshold = True

# ── Gemini globals (vision only) ─────────────────────────────
gemini_model   = None
selected_model = None
_GEMINI_MODELS = [
    "gemini-2.0-flash-exp", "gemini-2.0-flash",
    "gemini-1.5-flash", "gemini-1.5-flash-8b",
]
_gemini_limited: dict = {}
_gemini_key_idx = 0


# ============================================================
#  TTS ENGINE  (sentence-streaming like Alexa/Siri/Google)
# ============================================================

def _split_sentences(text: str) -> list:
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = []
    for s in raw:
        s = s.strip()
        if not s:
            continue
        if len(s) > 120:
            sub = re.split(r'(?<=[,;])\s+', s)
            sentences.extend(p.strip() for p in sub if p.strip())
        else:
            sentences.append(s)
    return sentences if sentences else [text.strip()]


async def _generate_bytes(text: str, lang: str) -> bytes:
    cfg  = VOICES.get(lang, VOICES["en-IN"])
    comm = edge_tts.Communicate(text, voice=cfg["voice"],
                                rate=cfg["rate"], pitch=cfg["pitch"])
    parts = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            parts.append(chunk["data"])
    return b"".join(parts)


def _synth(text: str, lang: str) -> bytes:
    key = f"{lang}::{text}"
    if key in _audio_cache:
        return _audio_cache[key]
    future = asyncio.run_coroutine_threadsafe(_generate_bytes(text, lang), _loop)
    return future.result(timeout=15)


def _play(data: bytes):
    sound   = pygame.mixer.Sound(io.BytesIO(data))
    channel = sound.play()
    while channel.get_busy():
        if not is_speaking.is_set():
            channel.stop()
            break
        time.sleep(0.02)


def speak(text: str, raw: bool = False):
    """Sentence-streaming speak. raw=True skips translation."""
    global current_language
    if not text or not text.strip():
        return

    lang = current_language

    if not raw and lang != "en-IN":
        text = _translate(text, lang)

    print(f"GHOST [{LANG_NAMES[lang]}]: {text}")

    sentences = _split_sentences(text)
    audio_q   = _queue.Queue(maxsize=2)
    DONE      = object()

    def _generator():
        for s in sentences:
            if not is_speaking.is_set():
                break
            try:
                audio_q.put(_synth(s, lang))
            except Exception as e:
                print(f"Synth error: {e}")
        audio_q.put(DONE)

    gen = threading.Thread(target=_generator, daemon=True, name="TTSGen")

    with tts_lock:
        is_speaking.set()
        gen.start()
        try:
            while True:
                try:
                    item = audio_q.get(timeout=20)
                except _queue.Empty:
                    print("TTS generator timed out.")
                    break
                if item is DONE or not is_speaking.is_set():
                    break
                _play(item)
        except Exception as e:
            print(f"TTS play error: {e}")
        finally:
            is_speaking.clear()

    gen.join(timeout=3)


def speak_raw(text: str):
    speak(text, raw=True)


def _pre_cache_phrases():
    def _gen():
        for phrase in QUICK_PHRASES.values():
            key = f"en-IN::{phrase}"
            if key not in _audio_cache:
                try:
                    f = asyncio.run_coroutine_threadsafe(
                        _generate_bytes(phrase, "en-IN"), _loop
                    )
                    _audio_cache[key] = f.result(timeout=10)
                    print(f"  Cached: '{phrase}'")
                except Exception as e:
                    print(f"  Cache miss '{phrase}': {e}")
    threading.Thread(target=_gen, daemon=True, name="PhraseCache").start()


def play_quick(key: str):
    phrase = QUICK_PHRASES.get(key, "")
    if not phrase or is_speaking.is_set():
        return
    lang = current_language
    if lang != "en-IN":
        speak(phrase)
        return
    cache_key = f"en-IN::{phrase}"
    if cache_key in _audio_cache:
        with tts_lock:
            is_speaking.set()
            try:
                _play(_audio_cache[cache_key])
            finally:
                is_speaking.clear()
    else:
        speak_raw(phrase)


# ============================================================
#  TRANSLATION  (uses call_ai — same provider chain)
# ============================================================

def _translate(text: str, target_lang: str) -> str:
    if target_lang == "en-IN":
        return text

    lang_name = LANG_NAMES[target_lang]
    cache_key = f"trans_{target_lang}_{hash(text)}"

    if cache_key in CACHE and (time.time() - CACHE[cache_key]["ts"]) < 3600:
        return CACHE[cache_key]["data"]

    prompt = f"Translate to {lang_name}. Return ONLY the translation, no quotes:\n{text}"
    result = call_ai(prompt, max_tokens=200)

    if result:
        CACHE[cache_key] = {"ts": time.time(), "data": result}
        return result
    return text


# ============================================================
#  MAIN AI RESPONDER
# ============================================================

def get_ai_response(prompt_en: str) -> str:
    """Get Ghost's response via provider chain. Returns text in current language."""
    return call_ai(prompt_en, max_tokens=120)


# ============================================================
#  GEMINI VISION WRAPPER  (camera only — not for text Q&A)
# ============================================================
_GEN_CFG = {"max_output_tokens": 300, "temperature": 0.7}
_GEMINI_RATE: dict = {}
_gemini_ki   = 0


def safe_generate_content(prompt_or_inputs):
    """Gemini wrapper used ONLY for camera/vision analysis."""
    global gemini_model, selected_model, _gemini_ki

    if not GEMINI_API_KEYS:
        return None

    n = len(GEMINI_API_KEYS)
    for ki_offset in range(n):
        ki  = (_gemini_ki + ki_offset) % n
        key = GEMINI_API_KEYS[ki]

        for model in _GEMINI_MODELS:
            slot = f"{ki}::{model}"
            if slot in _GEMINI_RATE and time.time() < _GEMINI_RATE[slot]:
                continue

            if ki != _gemini_ki or model != selected_model or gemini_model is None:
                try:
                    genai.configure(api_key=key)
                    gemini_model   = genai.GenerativeModel(model)
                    selected_model = model
                    _gemini_ki     = ki
                except Exception as e:
                    print(f"  Gemini load error {model}: {e}")
                    continue

            try:
                return gemini_model.generate_content(
                    prompt_or_inputs, generation_config=_GEN_CFG
                )
            except Exception as e:
                err = str(e)
                if "429" in err or "quota" in err.lower():
                    m = re.search(r'retry in (\d+(?:\.\d+)?)s', err)
                    secs = float(m.group(1)) if m else 60.0
                    _GEMINI_RATE[slot] = time.time() + secs
                    print(f"  [Gemini/{model}] quota {secs:.0f}s")
                    continue
                print(f"  [Gemini/{model}] error: {e}")
                return None
    return None


# ============================================================
#  LISTEN
# ============================================================

def listen_for_command() -> str:
    with sr.Microphone() as source:
        _recognizer.adjust_for_ambient_noise(source, duration=0.2)
        play_quick("ack")
        try:
            audio    = _recognizer.listen(source, timeout=6, phrase_time_limit=12)
            rec_lang = RECOGNITION_LANG.get(current_language, "en-IN")
            query    = _recognizer.recognize_google(audio, language=rec_lang)
            print(f"{USER_NAME} [{LANG_NAMES[current_language]}]: {query}")
            return query.lower()
        except sr.WaitTimeoutError:
            speak_raw("Nothing received.")
        except sr.UnknownValueError:
            speak_raw("Didn't catch that.")
        except sr.RequestError as e:
            speak_raw("Speech service error.")
            print(f"Recognition Error: {e}")
        return ""


# ============================================================
#  GREET
# ============================================================

def greet_user():
    hour = datetime.datetime.now().hour
    if   0  <= hour < 6:  g = "It's the middle of the night"
    elif 6  <= hour < 12: g = "Good morning"
    elif 12 <= hour < 18: g = "Good afternoon"
    else:                  g = "Good evening"
    speak_raw(f"{g}, {USER_NAME}. Ghost online. All systems green. Ready for orders.")


# ============================================================
#  SKILLS
# ============================================================

def play_song_on_youtube(song_name):
    speak(f"On it. Searching {song_name} on YouTube.")
    try:
        youtube  = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        req      = youtube.search().list(q=song_name, part='snippet', maxResults=1, type='video')
        response = req.execute()
        if response.get('items'):
            item = response['items'][0]
            webbrowser.open(f"https://www.youtube.com/watch?v={item['id']['videoId']}")
            speak(f"Playing {item['snippet']['title']}.")
        else:
            webbrowser.open(f"https://www.youtube.com/results?search_query={song_name}")
    except Exception as e:
        webbrowser.open(f"https://www.youtube.com/results?search_query={song_name}")
        print(f"YouTube Error: {e}")


def get_weather(city_name="Mumbai"):
    ck = f"weather_{city_name.lower()}"
    now = time.time()
    if ck in CACHE and (now - CACHE[ck]['ts']) < CACHE_EXPIRY_SECONDS:
        speak(CACHE[ck]['data']); return
    speak(f"Checking weather for {city_name}.")
    try:
        data = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city_name}&appid={WEATHER_API_KEY}&units=metric", timeout=5
        ).json()
        if data.get("cod") != "404":
            rep = f"{city_name}: {data['weather'][0]['description']}, {data['main']['temp']:.1f}°C."
            CACHE[ck] = {'ts': now, 'data': rep}
            speak(rep)
        else:
            speak(f"No weather data for {city_name}.")
    except Exception:
        speak("Weather service unreachable.")


def open_application_or_website(target_name):
    tl = target_name.lower()
    done = False
    if any(x in tl for x in ['.com','.org','.net','.in','.io','.co']) or tl.startswith('www.'):
        webbrowser.open(target_name if tl.startswith(('http://','https://')) else f"https://{target_name}")
        done = True
    else:
        special = {
            "store":"ms-windows-store:", "edge":"microsoft-edge:", "whatsapp":"whatsapp:",
            "mail":"mailto:", "calendar":"outlookcal:", "photos":"ms-photos:",
            "settings":"ms-settings:", "camera":"microsoft.windows.camera:",
        }
        for kw, proto in special.items():
            if kw in tl:
                os.system(f'start {proto}'); done = True; break
        if not done and tl in APP_PATHS and os.path.exists(APP_PATHS[tl]):
            os.startfile(APP_PATHS[tl]); done = True
        if not done:
            os.system(f'start "" "{target_name}"'); done = True
    speak(f"Opening {target_name}." if done else f"Can't find {target_name}.")


def tell_joke():
    try:
        r = requests.get(
            "https://v2.jokeapi.dev/joke/Any"
            "?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single",
            timeout=4
        ).json()
        if not r.get('error'):
            joke = _translate(r['joke'], current_language) if current_language != "en-IN" else r['joke']
            speak_raw(joke)
        else:
            speak("No jokes today.")
    except Exception:
        speak("Joke service offline.")


def web_search(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak(f"Searching for {query}.")


def search_wikipedia(query):
    speak(f"Checking Wikipedia for {query}.")
    try:
        speak(wikipedia.summary(query, sentences=2))
    except Exception:
        speak(f"Wikipedia has nothing on {query}.")


def get_system_stats():
    cpu  = psutil.cpu_percent(interval=0.5)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    bat  = psutil.sensors_battery()
    rep  = (f"CPU at {cpu}%. RAM: {ram.percent}% used, "
            f"{ram.available//(1024**2)}MB free. Disk: {disk.percent}% used.")
    if bat:
        rep += f" Battery: {bat.percent:.0f}%, {'charging' if bat.power_plugged else 'discharging'}."
    speak(rep)


def take_screenshot():
    try:
        ts   = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fn   = f"Screenshot_{ts}.png"
        d1   = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
        d2   = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        desk = d1 if os.path.exists(d1) else d2
        os.makedirs(desk, exist_ok=True)
        pyautogui.screenshot().save(os.path.join(desk, fn))
        speak(f"Screenshot saved: {fn}")
    except Exception as e:
        speak("Screenshot failed."); print(f"Screenshot error: {e}")


def get_news():
    speak("Pulling latest headlines.")
    try:
        data = requests.get(
            f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}", timeout=5
        ).json()
        articles = data.get("articles", [])[:3] if data.get("status") == "ok" else []
        for a in articles:
            speak(a['title'])
        if not articles:
            speak("No headlines found.")
    except Exception:
        speak("News service unreachable.")


def analyze_camera_view(question="What do you see?"):
    if not gemini_model and not GEMINI_API_KEYS:
        speak("Vision module offline.")
        return
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Can't access camera.")
        return
    speak_raw("Camera on. C to capture, Q to quit.")
    captured = None
    while True:
        ret, frame = cap.read()
        if not ret: break
        cv2.imshow("Ghost Vision — C:capture  Q:quit", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            captured = frame; speak_raw("Analyzing."); break
        elif key == ord('q'):
            speak_raw("Camera off."); break
    cap.release(); cv2.destroyAllWindows()
    if captured is not None:
        try:
            pil  = Image.fromarray(cv2.cvtColor(captured, cv2.COLOR_BGR2RGB))
            full_q = f"{question} Respond in {LANG_NAMES[current_language]}."
            resp = safe_generate_content([full_q, pil])
            if resp:
                speak_raw(resp.text)
        except Exception as e:
            speak("Vision analysis failed."); print(f"Vision Error: {e}")


def set_reminder(command):
    speak("What should I remind you about?")
    text = listen_for_command()
    if not text: speak("Reminder cancelled."); return
    nums = re.findall(r'\d+', command)
    if not nums: speak("Tell me the time amount."); return
    val = int(nums[0])
    if "minute" in command:
        delay = val * 60; speak(f"Reminder in {val} minutes.")
    elif "second" in command:
        delay = val; speak(f"Reminder in {val} seconds.")
    else:
        speak("Say minutes or seconds."); return
    def _fire():
        time.sleep(delay); speak(f"{USER_NAME}. Reminder: {text}")
    threading.Thread(target=_fire, daemon=True).start()


def get_location():
    try:
        d = requests.get('https://ipinfo.io/json', timeout=4).json()
        speak(f"You're in {d.get('city')}, {d.get('region')}, {d.get('country')}.")
    except Exception:
        speak("Can't determine location.")


def run_speed_test():
    speak("Running speed test. Hold on.")
    try:
        st = speedtest.Speedtest(); st.get_best_server()
        dl = st.download()/1_000_000; ul = st.upload()/1_000_000; p = st.results.ping
        speak(f"Download: {dl:.1f} Mbps. Upload: {ul:.1f} Mbps. Ping: {p:.0f} ms.")
    except Exception as e:
        speak("Speed test failed."); print(f"Speedtest Error: {e}")


def calculate(expr_text: str):
    expr = (expr_text.replace('calculate','').replace('what is','').strip()
            .replace('plus','+').replace('minus','-')
            .replace('times','*').replace('multiplied by','*').replace('divided by','/'))
    try:
        result = eval("".join(c for c in expr if c in "0123456789.+-*/() "))
        speak(f"Answer: {result}")
    except Exception:
        speak("Couldn't solve that.")


def show_and_tell(query):
    speak(f"Looking up {query}.")
    img_dir = "temp_images"
    os.makedirs(img_dir, exist_ok=True)
    try:
        url  = f"https://www.google.com/search?q={requests.utils.quote(query)}&tbm=isch"
        hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=hdrs, timeout=6)
        img_url = None
        for b in re.findall(r'\["(\S+)",\d+,\d+\]', resp.text):
            dec = bytes(b,"utf-8").decode("unicode_escape")
            if dec.startswith("http") and any(x in dec for x in [".jpg",".jpeg",".png"]):
                img_url = dec; break
        if not img_url: speak("No image found."); return
        tmp = os.path.join(img_dir, "display.jpg")
        with open(tmp,'wb') as f: f.write(requests.get(img_url, headers=hdrs, timeout=6).content)
        img = cv2.imread(tmp)
        if img is not None:
            cv2.imshow(f"Ghost: {query} — any key to close", img)
            cv2.waitKey(0); cv2.destroyAllWindows()
        else:
            speak("Couldn't display image.")
    except Exception as e:
        speak("Image search failed."); print(f"Image Error: {e}")
    finally:
        shutil.rmtree(img_dir, ignore_errors=True)


def find_song_by_lyrics(lyrics):
    speak("Checking lyrics.")
    prompt = f"Lyrics: '{lyrics}'. Reply ONLY as: 'Song Title by Artist Name'."
    result = call_ai(prompt, max_tokens=60)
    if result and 'by' in result.lower() and len(result) < 100:
        speak(f"That's {result}. Playing now.")
        play_song_on_youtube(result)
    else:
        play_song_on_youtube(lyrics)


def control_volume(command):
    try:
        vol = cast(
            AudioUtilities.GetSpeakers().Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None),
            POINTER(IAudioEndpointVolume)
        )
        cur = vol.GetMasterVolumeLevelScalar()
        if 'up' in command or 'increase' in command:
            nv = min(1.0, cur+0.1); vol.SetMasterVolumeLevelScalar(nv,None); speak(f"Volume {int(nv*100)}%.")
        elif 'down' in command or 'decrease' in command:
            nv = max(0.0, cur-0.1); vol.SetMasterVolumeLevelScalar(nv,None); speak(f"Volume {int(nv*100)}%.")
        elif 'max' in command or 'full' in command:
            vol.SetMasterVolumeLevelScalar(1.0,None); speak("Max volume.")
        elif 'mute' in command:
            vol.SetMute(1,None); speak("Muted.")
        elif 'unmute' in command:
            vol.SetMute(0,None); speak("Unmuted.")
        else:
            nums = re.findall(r'\d+', command)
            if nums:
                lv = int(nums[0]); vol.SetMasterVolumeLevelScalar(lv/100.0,None); speak(f"Volume {lv}%.")
    except Exception as e:
        speak("Volume control failed."); print(f"Volume Error: {e}")


def generate_password():
    pw = ''.join(random.choice(string.ascii_letters+string.digits+string.punctuation) for _ in range(16))
    print(f"Password: {pw}"); speak("Password generated. Check console.")


def roll_dice():
    speak(f"Rolled a {random.randint(1,6)}.")

def flip_coin():
    speak(f"{random.choice(['Heads','Tails'])}.")


# ============================================================
#  COMMAND PROCESSOR
# ============================================================

def process_command(command: str):
    if not command: return
    if not _command_lock.acquire(blocking=False):
        print(f"[CMD SKIPPED]: {command}"); return
    try:
        _process(command)
    finally:
        _command_lock.release()


def _process(command: str):
    global current_language

    # ── Language ────────────────────────────────────────────
    if any(x in command for x in ["speak in hindi","answer in hindi","switch to hindi"]):
        current_language = "hi-IN"; speak_raw("ठीक है, अब मैं हिंदी में बात करूँगा।"); return
    if any(x in command for x in ["speak in marathi","answer in marathi","switch to marathi"]):
        current_language = "mr-IN"; speak_raw("ठीक आहे, आता मी मराठीत बोलेन."); return
    if any(x in command for x in ["speak in english","answer in english","switch to english","back to english"]):
        current_language = "en-IN"; speak_raw("Copy that. Back to English."); return

    # ── Wikipedia ──────────────────────────────────────────
    if command.startswith('search wikipedia for') or command.startswith('wikipedia'):
        search_wikipedia(command.replace('search wikipedia for','').replace('wikipedia','').strip())

    # ── Web search ─────────────────────────────────────────
    elif command.startswith('search for') or command.startswith('search'):
        web_search(command.replace('search for','').replace('search','').strip())

    # ── YouTube ────────────────────────────────────────────
    elif command.startswith('play'):
        play_song_on_youtube(command.replace('play','').strip())

    # ── Open ───────────────────────────────────────────────
    elif command.startswith('open'):
        open_application_or_website(command.replace('open','').strip())

    # ── Time / Date ────────────────────────────────────────
    elif any(x in command for x in ["what's the time","what is the time","current time"]):
        speak(f"It's {datetime.datetime.now().strftime('%I:%M %p')}.")
    elif any(x in command for x in ["what's the date","what is the date","today's date"]):
        speak(f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}.")

    # ── Weather ────────────────────────────────────────────
    elif 'weather' in command:
        get_weather(command.split(" in ")[-1].strip() if " in " in command else "Mumbai")

    # ── Maps ───────────────────────────────────────────────
    elif 'search on map' in command or 'find on map' in command:
        loc = re.sub(r'search on map|find on map','',command).strip()
        webbrowser.open(f"https://www.google.com/maps/search/{loc}")
        speak(f"Locating {loc}.")

    # ── Joke ───────────────────────────────────────────────
    elif 'joke' in command:
        tell_joke()

    # ── Creator ────────────────────────────────────────────
    elif any(x in command for x in ['who made you','who created you','your creator']):
        speak(f"Built by {USER_CREATOR}. Good operator.")

    # ── System status ──────────────────────────────────────
    elif any(x in command for x in ['system status','status report','system report']):
        get_system_stats()

    # ── Screenshot ─────────────────────────────────────────
    elif 'screenshot' in command or 'capture the screen' in command:
        take_screenshot()

    # ── News ───────────────────────────────────────────────
    elif 'news' in command or 'headlines' in command:
        get_news()

    # ── Thank you ──────────────────────────────────────────
    elif 'thank you' in command or 'thanks' in command:
        speak("Anytime.")

    # ── Vision ─────────────────────────────────────────────
    elif 'read the text' in command or 'what does this say' in command:
        analyze_camera_view("Read all text in this image.")
    elif 'what emotion' in command or 'how do i look' in command:
        analyze_camera_view("Describe the emotion on the person's face.")
    elif command.startswith('count the') or command.startswith('how many'):
        analyze_camera_view(f"Answer: {command}")
    elif 'how old do i look' in command or 'what is my age' in command:
        analyze_camera_view("Estimate age of person in this image.")
    elif 'solve this' in command:
        analyze_camera_view("Solve the math problem in this image.")
    elif 'story about this' in command:
        analyze_camera_view("Create a short story about this scene.")
    elif any(x in command for x in ['what do you see','describe what you see','analyze this']):
        analyze_camera_view()
    elif 'what is this' in command or 'identify this' in command:
        analyze_camera_view(f"Identify main object. User asked: {command}")
    elif 'take a picture' in command:
        analyze_camera_view("Describe this scene in detail.")

    # ── Show & Tell ────────────────────────────────────────
    elif ('show me' in command or 'picture of' in command
          or ('what does' in command and 'look like' in command)):
        query = (command.replace('show me a','').replace('show me an','').replace('show me','')
                        .replace('picture of a','').replace('picture of an','').replace('picture of','')
                        .replace('what does a','').replace('what does an','').replace('what does','')
                        .replace('look like','').strip())
        show_and_tell(query)

    # ── Song ID ────────────────────────────────────────────
    elif any(x in command for x in ['find this song','what song is this','identify the song']):
        speak("Sing a line.")
        lyrics = listen_for_command()
        if lyrics: find_song_by_lyrics(lyrics)

    # ── Abilities ──────────────────────────────────────────
    elif 'what can you do' in command or 'your abilities' in command:
        speak("Search web, play YouTube, check weather, read news, control volume, "
              "take screenshots, analyze camera, set reminders, speed tests, open apps, and more.")

    # ── System control ─────────────────────────────────────
    elif 'shutdown system' in command:
        speak("Confirm shutdown?")
        if 'yes' in listen_for_command():
            speak("Shutting down."); subprocess.call('shutdown /s /t 1', shell=True)
        else: speak("Cancelled.")
    elif 'restart system' in command:
        speak("Confirm restart?")
        if 'yes' in listen_for_command():
            speak("Restarting."); subprocess.call('shutdown /r /t 1', shell=True)
        else: speak("Cancelled.")
    elif 'lock system' in command or 'lock screen' in command:
        speak("Locking."); subprocess.call('rundll32.exe user32.dll,LockWorkStation', shell=True)

    # ── Volume ─────────────────────────────────────────────
    elif 'volume' in command:
        control_volume(command)

    # ── Utilities ──────────────────────────────────────────
    elif 'generate a password' in command or 'create a password' in command:
        generate_password()
    elif 'roll' in command and 'dice' in command:
        roll_dice()
    elif 'flip' in command and 'coin' in command:
        flip_coin()

    # ── Reminder ───────────────────────────────────────────
    elif 'reminder' in command or 'remind me' in command:
        set_reminder(command)

    # ── Location ───────────────────────────────────────────
    elif 'my location' in command or 'where am i' in command or 'where are we' in command:
        get_location()

    # ── Speed test ─────────────────────────────────────────
    elif 'speed test' in command or 'internet speed' in command:
        run_speed_test()

    # ── Calculator ─────────────────────────────────────────
    elif 'calculate' in command or (
        any(op in command for op in ['+','-','*','/']) and any(c.isdigit() for c in command)
    ):
        calculate(command)

    # ── Exit ───────────────────────────────────────────────
    elif any(x in command for x in ['goodbye','exit','go offline','shut down ghost']):
        speak_raw("Ghost going dark. Stay sharp.")
        time.sleep(2); stop_assistant.set()

    # ── AI fallback ────────────────────────────────────────
    else:
        ck = f"ai_{current_language}_{command}"
        if ck in CACHE and (time.time() - CACHE[ck]['ts']) < CACHE_EXPIRY_SECONDS:
            speak_raw(CACHE[ck]['data']); return
        play_quick("thinking")
        answer = get_ai_response(command)
        if answer:
            CACHE[ck] = {'ts': time.time(), 'data': answer}
            speak_raw(answer)
        else:
            slots = list(_provider_limited.values())
            if slots:
                wait = max(0, int(min(slots) - time.time()))
                speak_raw(f"All AI providers on cooldown. Try again in {wait} seconds.")
            else:
                speak_raw("Can't reach any AI right now. Check your API keys.")


# ============================================================
#  BACKGROUND LISTENER
# ============================================================

def background_listener_callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language="en-IN").lower()
        print(f"[BG heard]: {text}")

        stop_cmds = ["stop","shut up","enough","cancel","be quiet","silence"]
        if is_speaking.is_set() and any(c in text for c in stop_cmds):
            is_speaking.clear(); pygame.mixer.stop(); return

        wake_words = [ASSISTANT_NAME, "hey ghost", "okay ghost", "ghost"]
        triggered  = next((w for w in wake_words if text.startswith(w)), None)

        if triggered:
            inline = text.replace(triggered, "", 1).strip()
            if inline:
                threading.Thread(target=process_command, args=(inline,), daemon=True).start()
            else:
                def _listen_and_process():
                    cmd = listen_for_command()
                    if cmd: process_command(cmd)
                threading.Thread(target=_listen_and_process, daemon=True).start()

    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print(f"BG listener error: {e}")


# ============================================================
#  MAIN
# ============================================================

def main():
    global gemini_model, selected_model

    print("\n" + "▓"*60)
    print("  G H O S T  —  Tactical AI Assistant")
    print(f"  Operator: {USER_CREATOR}")
    print("▓"*60)

    # Show which providers are configured
    print("\n  AI Providers:")
    for p in PROVIDERS:
        key = globals().get(p["key_var"],"")
        status = "✓ configured" if _key_valid(key) else "✗ no key"
        print(f"    {p['name']:12} {status}")
    print()

    _pre_cache_phrases()

    # Init Gemini for vision
    try:
        genai.configure(api_key=GEMINI_API_KEYS[0])
        supported = set(m.name.split("/")[-1] for m in genai.list_models()
                        if "generateContent" in m.supported_generation_methods)
        for name in _GEMINI_MODELS:
            if name in supported:
                gemini_model   = genai.GenerativeModel(name)
                selected_model = name
                print(f"  Gemini vision: {name} ✓")
                break
    except Exception as e:
        print(f"  Gemini vision: offline ({e})")

    greet_user()

    mic = sr.Microphone()
    with mic as source:
        print("Calibrating mic...")
        _recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready.\n")

    speak_raw(f"Listening, {USER_NAME}. Say 'Ghost' to activate.")

    stop_listening = _recognizer.listen_in_background(
        mic, background_listener_callback, phrase_time_limit=12
    )

    stop_assistant.wait()

    print("\nGhost offline.")
    stop_listening(wait_for_stop=False)
    pygame.mixer.quit()


if __name__ == "__main__":
    main()
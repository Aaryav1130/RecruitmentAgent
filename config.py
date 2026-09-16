import os
from dotenv import load_dotenv

load_dotenv()

# API keys
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
SERPAPI_API_KEY=os.getenv("SERPAPI_API_KEY")

import requests

# Priority list of models to try, ordered by preference (largest context first)
# These are the models known to work on Groq free tier as of 2026
_MODEL_PRIORITY = [
    "meta-llama/llama-4-scout-17b-16e-instruct",  # 131K context
    "qwen/qwen3-32b",                              # 32K context
    "mistral-saba-24b",                             # 32K context
    "llama-3.3-70b-versatile",                      # 128K context
    "llama-3.1-8b-instant",                         # 128K context (deprecated but try)
    "openai/gpt-oss-20b",                           # 16K context
]

def get_valid_groq_model():
    """Dynamically find the best available Groq model by querying the API."""
    available_ids = set()
    try:
        if GROQ_API_KEY:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            resp = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                available_ids = {m["id"] for m in models}
                print(f"✅ Groq API returned {len(available_ids)} available models: {sorted(available_ids)}")

                # 1. Try our priority list first
                for model_id in _MODEL_PRIORITY:
                    if model_id in available_ids:
                        print(f"✅ Selected model from priority list: {model_id}")
                        return model_id

                # 2. Fallback: pick the first chat model that's NOT a whisper/tts/image model
                skip_prefixes = ("whisper", "distil-whisper", "playai", "orpheus", "compound")
                for m in models:
                    mid = m["id"]
                    if not any(mid.startswith(p) for p in skip_prefixes):
                        print(f"⚠️ Using fallback model: {mid}")
                        return mid

                # 3. Last resort: first model in the list
                if models:
                    print(f"⚠️ Using last-resort model: {models[0]['id']}")
                    return models[0]["id"]
            else:
                print(f"⚠️ Groq /models returned status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"⚠️ Dynamic model fetch failed: {e}")

    # If everything fails, return this as the static fallback
    return "meta-llama/llama-4-scout-17b-16e-instruct"

# Model settings
LLM_MODEL = get_valid_groq_model()
print(f"🔧 LLM_MODEL = {LLM_MODEL}")


# Job search settings
DEFAULT_JOB_COUNT=5
JOB_PLATFORMS=["LinkedIn","Indeed","Glassdoor","Naukri"]

COLORS={
    # Primary palette
    "primary": "#1C4E80",      # Dark blue for main elements and headers
    "secondary": "#0091D5",    # Medium blue for secondary elements
    "tertiary": "#6BB4C0",     # Teal blue for tertiary elements

    # Semantic names (replacing old numeric names for clarity)
    "success_dark": "#074A04",     # was "fourth"
    "success_light": "#29BE1E",    # was "fifth"
    "success_bg": "#0B4007",       # was "sixth"
    "purple_accent": "#6C5ACB",    # was "seventh"
    "navy": "#144D76",             # was "eighth"
    "danger_dark": "#950909",      # was "ninth" (was misspelled as "nineth")
    "blue_deep": "#033c84",        # was "tenth"
    "gray_light": "#cdcdcd",       # was "eleventh"

    # Backward compatibility aliases (so existing code doesn't break)
    "fourth": "#074A04",
    "fifth": "#29BE1E",
    "sixth": "#0B4007",
    "seventh": "#6C5ACB",
    "eighth": "#144D76",
    "nineth": "#950909",
    "tenth": "#033c84",
    "eleventh": "#cdcdcd",

    # Interview question card colors
    "question": "#E46767",
    "context": "#9AA9B7",
    "approach": "#B6D7B6",
    "tips": "#EAD5AD",

    # Accent colors
    "accent": "#F17300",       # Orange for highlighting
    "accent1": "#3E7CB1",      # Steel blue for subtler accents
    "accent2": "#44BBA4",      # Seafoam for highlighting information
    "accent3": "#F17300",      # Orange for call-to-action buttons

    # Functional colors
    "success": "#26A69A",      # Teal green for success messages
    "warning": "#F9A825",      # Golden yellow for warnings
    "error": "#E53935",        # Bright red for errors
    "info": "#0277BD",         # Information blue

    # Background and text - Basic professional style
    "background": "#F5F7FA",   # Light blue-gray for backgrounds
    "card_bg": "#FFFFFF",      # White for card backgrounds
    "text": "#FFFFFF",         # White for text on dark background
    "text_dark": "#000000",    # Black for text on light background
    "text_light": "#333333",   # Dark gray for secondary text
    "text_red": "#FF5252",     # Red Color for high-contrast text
    "panel_bg": "#F0F5FF"      # Light blue background for panels
}

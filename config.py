import os
from dotenv import load_dotenv

load_dotenv()

# API keys
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
SERPAPI_API_KEY=os.getenv("SERPAPI_API_KEY")

# Model settings
# LLM_MODEL="llama-3.1-8b-instant"
LLM_MODEL="meta-llama/llama-4-scout-17b-16e-instruct"
# LLM_MODEL="moonshotai/kimi-k2-instruct"
# LLM_MODEL="qwen3:4b-instruct"
# LLM_MODEL="qwen2.5:1.5b-instruct"
# LLM_MODEL="qwen2.5:0.5b-instruct"


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

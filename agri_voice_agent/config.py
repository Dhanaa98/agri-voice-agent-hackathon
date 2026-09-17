import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "Colombo,LK")

FARM_STATE_PATH = PROJECT_ROOT / "agri_voice_agent" / "farm_state.json"
WAKEWORD_MODELS_DIR = PROJECT_ROOT / "agri_voice_agent" / "wakeword" / "models"

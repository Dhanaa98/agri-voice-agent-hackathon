import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "Colombo,LK")

# elevenlabs-tts branch only (not on master): cloud TTS for spoken replies,
# instead of the browser's own free speechSynthesis -- see tts_client.py.
# ELEVENLABS_VOICE_ID has no default on purpose: a wrong/guessed voice_id
# would fail at request time with a confusing error, and which voices
# exist depends on the account -- get a real one from
# https://elevenlabs.io/app/voice-library (or the account's own Voices
# list) rather than assume a premade voice is still available.
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

FARM_STATE_PATH = PROJECT_ROOT / "agri_voice_agent" / "farm_state.json"
WAKEWORD_MODELS_DIR = PROJECT_ROOT / "agri_voice_agent" / "wakeword" / "models"

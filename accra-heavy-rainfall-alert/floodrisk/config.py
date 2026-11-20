"""Project settings in one place. Change values here, not in other files."""
from pathlib import Path

# The folder that contains the whole project
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Files created by the notebook and copied into this repo
MODEL_PATH = PROJECT_ROOT / "models" / "flood_model_v2.pkl"
SETTINGS_PATH = PROJECT_ROOT / "models" / "settings.json"
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "model_features_v2.csv"

# Greater Accra region code in the HDX rainfall file
PLACE_CODE = "GH07"

# Column names used in the processed feature table
DATE_COLUMN = "date"
TARGET_COLUMN = "next_heavy_b"   # 1 if the next 10-day period was heavy rain

# Shown on the dashboard's About page. Replace both placeholders before you deploy.
CONTACT_EMAIL = "[add your ALU email here]"
DATA_ATTRIBUTION = "[copy the attribution and licence text from the HDX dataset page]"

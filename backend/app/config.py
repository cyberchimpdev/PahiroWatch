import os
from pathlib import Path
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv("DATABASE_PATH", str(Path.cwd() / "pahirowatch.db"))

HACKATHON_KEY = os.getenv("HACKATHON_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# Corridor & Pilot Setting
DEFAULT_CORRIDOR_ID = os.getenv("DEFAULT_CORRIDOR_ID", "NH05-MUG")
OPERATOR_NAME = os.getenv("OPERATOR_NAME", "Ramesh, Municipal Disaster Management Officer")
MUNICIPALITY_NAME = os.getenv("MUNICIPALITY_NAME", "Ichhyakamana Rural Municipality")

# Autonomous Trigger Thresholds
RAINFALL_TRIGGER_THRESHOLD_24H_MM = 100.0  # Wakes agent if 24h rainfall exceeds 100mm
SLOPE_HIGH_RISK_DEG = 30.0                # Slopes above 30 degrees considered high hazard

# NPR Cost Exchange Rate Estimation (1 USD ~ 135 NPR)
USD_TO_NPR_RATE = 135.0
COST_PER_1K_PROMPT_TOKENS_USD = 0.00015
COST_PER_1K_COMPLETION_TOKENS_USD = 0.00060

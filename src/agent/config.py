from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Studio API init.
UST_API_KEY = os.getenv("UST_API_KEY")

UST_PROJ_ID = os.getenv("UST_PROJ_ID")
UST_HEADER = {"x-project-id": UST_PROJ_ID}

UST_AGNT_ID = os.getenv("UST_AGNT_ID")
UST_CNFG_ID = os.getenv("UST_CNFG_ID", "1")


# DIRS
BASE_DIR = Path(__file__).resolve().parent


# Check if the required environment variables are set.
def check_envs():
    if not UST_API_KEY:
        raise ValueError("UST_API_KEY is not set in the environment variables.")
    if not UST_PROJ_ID:
        raise ValueError("UST_PROJ_ID is not set in the environment variables.")
    if not UST_AGNT_ID:
        raise ValueError("UST_AGNT_ID is not set in the environment variables.")

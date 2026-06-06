import os
from datetime import datetime

LOG_PATH = "/app/logs"
LOG_FILE = f"{LOG_PATH}/audit.log"

os.makedirs(LOG_PATH, exist_ok=True)

def log_event(message: str):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

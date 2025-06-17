import json
import os
from datetime import datetime

SAVE_PATH = "processed_orders.json"

def save_json(data: dict):
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "timestamp": timestamp,
        "data": data
    }

    # If file exists, load and append; else, create new
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r+") as file:
            try:
                existing = json.load(file)
            except json.JSONDecodeError:
                existing = []

            existing.append(entry)
            file.seek(0)
            json.dump(existing, file, indent=4)
    else:
        with open(SAVE_PATH, "w") as file:
            json.dump([entry], file, indent=4)

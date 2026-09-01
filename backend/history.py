import json
import os
from datetime import datetime

HISTORY_FILE = "query_history.json"


def load_history():
    """Load previous query history."""
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_query(question, sql, execution_time, success):
    """Save a new query into history."""
    history = load_history()

    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "sql": sql,
        "execution_time": round(execution_time, 3),
        "success": success
    })

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def get_history():
    return load_history()
import os
import json

def inicializar_feedback_json(path="feedback.json"):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
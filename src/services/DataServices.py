from pathlib import Path
import json

class DataServices:
    def __init__(self):
        self.name = "data.json"
        self.path = Path("./storage/" + self.name)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def get_init_data(self):
        if not self.path.exists():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, EOFError, FileNotFoundError):
            return {}

    def save_data(self, data):
        with open(self.path, "w", encoding="utf-8" ) as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
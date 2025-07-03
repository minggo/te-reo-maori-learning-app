import json
from importlib.resources import files

def load_words_from_file():
    # returns a Python list of dicts
    data = files("app.data").joinpath("words.json").read_text(encoding="utf-8")
    return json.loads(data)
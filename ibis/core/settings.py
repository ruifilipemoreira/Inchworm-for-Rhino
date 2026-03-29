import json
import os

_SETTINGS_DIR  = os.path.join(os.path.expanduser("~"), ".ibis")
_SETTINGS_FILE = os.path.join(_SETTINGS_DIR, "settings.json")

DEFAULTS = {
    "scale_numerator":   "1",
    "scale_denominator": "100",
    "real_unit_index":   2,
    "model_unit_index":  0,
}


def load():
    try:
        with open(_SETTINGS_FILE, "r") as f:
            return {**DEFAULTS, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(DEFAULTS)


def save(data):
    try:
        os.makedirs(_SETTINGS_DIR, exist_ok=True)
        with open(_SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass
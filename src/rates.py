import json
import os

# Rates in percent. Edit them in the app with "Change the Rate of Interest",
# and verify them against India Post for the current quarter.
DEFAULTS = {
    "RD": 6.7,
    "PPF": 7.1,
    "SSA": 8.2,
    "1 Year TD": 6.9,
    "2 Year TD": 6.9,
    "3 Year TD": 7.0,
    "5 Year TD": 7.5,
    "NSC": 7.7,
    "KVP": 7.5,
    "MIS": 7.4,
    "SCSS": 8.2,
}


def _path():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    folder = os.path.join(base, "PostOfficeCalc")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "rates.json")


class Rates:
    def __init__(self):
        self.data = dict(DEFAULTS)
        try:
            with open(_path(), "r", encoding="utf-8") as f:
                self.data.update(json.load(f))
        except Exception:
            pass

    def get(self, name):
        """Return the rate as a decimal (7.5 -> 0.075)."""
        return float(self.data.get(name, DEFAULTS.get(name, 0))) / 100.0

    def save(self):
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

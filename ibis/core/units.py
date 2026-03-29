UNITS_TO_METERS = {
    "Millimeters (mm)": 0.001,
    "Centimeters (cm)": 0.01,
    "Meters (m)":       1.0,
    "Inches (in)":      0.0254,
    "Feet (ft)":        0.3048,
}

UNIT_KEYS     = list(UNITS_TO_METERS.keys())
PRESET_SCALES = ["1:20", "1:50", "1:100", "1:200", "1:500", "1:1000"]


def to_meters(value, unit_label):
    return float(value) * UNITS_TO_METERS[unit_label]


def from_meters(value_in_meters, unit_label):
    return value_in_meters / UNITS_TO_METERS[unit_label]


def format_number(value):
    return f"{value:.4f}".rstrip("0").rstrip(".")


def extract_abbreviation(unit_label):
    return unit_label[unit_label.index("(") + 1 : unit_label.index(")")]
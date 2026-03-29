PROCESS_DATA = {
    "Laser Cut": {
        "materials": {
            "Acrylic":   {"kerf": 0.2,  "tolerance": 0.1},
            "MDF / Wood":{"kerf": 0.3,  "tolerance": 0.15},
            "Cardboard": {"kerf": 0.1,  "tolerance": 0.1},
            "Steel":     {"kerf": 0.5,  "tolerance": 0.2},
            "Aluminum":  {"kerf": 0.4,  "tolerance": 0.15},
            "Plywood":   {"kerf": 0.25, "tolerance": 0.15},
        },
        "has_kerf": True,
    },
    "CNC Milling": {
        "materials": {
            "MDF / Wood": {"kerf": 0.0, "tolerance": 0.1},
            "Plywood":    {"kerf": 0.0, "tolerance": 0.1},
            "Foam":       {"kerf": 0.0, "tolerance": 0.5},
            "Aluminum":   {"kerf": 0.0, "tolerance": 0.05},
            "Steel":      {"kerf": 0.0, "tolerance": 0.05},
            "Plastic":    {"kerf": 0.0, "tolerance": 0.1},
        },
        "has_kerf": False,
    },
    "3D Print — FDM": {
        "materials": {
            "PLA":  {"kerf": 0.0, "tolerance": 0.3},
            "ABS":  {"kerf": 0.0, "tolerance": 0.4},
            "PETG": {"kerf": 0.0, "tolerance": 0.3},
            "TPU":  {"kerf": 0.0, "tolerance": 0.5},
            "ASA":  {"kerf": 0.0, "tolerance": 0.35},
        },
        "has_kerf": False,
    },
    "3D Print — SLA / DLP": {
        "materials": {
            "Standard Resin":  {"kerf": 0.0, "tolerance": 0.1},
            "ABS-like Resin":  {"kerf": 0.0, "tolerance": 0.1},
            "Flexible Resin":  {"kerf": 0.0, "tolerance": 0.2},
            "Castable Resin":  {"kerf": 0.0, "tolerance": 0.15},
        },
        "has_kerf": False,
    },
    "Sheet Metal Bending": {
        "materials": {
            "Steel 1mm":    {"kerf": 0.0, "tolerance": 0.3,  "bend_radius": 1.5},
            "Steel 2mm":    {"kerf": 0.0, "tolerance": 0.5,  "bend_radius": 3.0},
            "Steel 3mm":    {"kerf": 0.0, "tolerance": 0.8,  "bend_radius": 4.5},
            "Aluminum 1mm": {"kerf": 0.0, "tolerance": 0.25, "bend_radius": 1.0},
            "Aluminum 2mm": {"kerf": 0.0, "tolerance": 0.4,  "bend_radius": 2.0},
            "Aluminum 3mm": {"kerf": 0.0, "tolerance": 0.6,  "bend_radius": 3.0},
        },
        "has_kerf": False,
    },
}

PROCESS_KEYS = list(PROCESS_DATA.keys())


def get_material_keys(process_label):
    return list(PROCESS_DATA[process_label]["materials"].keys())


def get_process_data(process_label):
    return PROCESS_DATA[process_label]


def compute_tolerance_result(process_label, material_label, nominal_mm):
    process  = PROCESS_DATA[process_label]
    material = process["materials"][material_label]

    tolerance  = material["tolerance"]
    kerf       = material["kerf"]
    has_kerf   = process["has_kerf"]
    bend_radius = material.get("bend_radius")

    dim_min = nominal_mm - tolerance
    dim_max = nominal_mm + tolerance

    result = {
        "nominal":     nominal_mm,
        "tolerance":   tolerance,
        "dim_min":     dim_min,
        "dim_max":     dim_max,
        "has_kerf":    has_kerf,
        "kerf":        kerf,
        "bend_radius": bend_radius,
    }

    if has_kerf:
        result["kerf_compensated"] = nominal_mm + (kerf / 2.0)

    return result


def format_result_for_log(process_label, material_label, result):
    lines = [
        f"Ibis Tolerance — {process_label} / {material_label}",
        f"  Nominal:    {result['nominal']:.3f} mm",
        f"  Tolerance:  ± {result['tolerance']:.3f} mm",
        f"  Min:        {result['dim_min']:.3f} mm",
        f"  Max:        {result['dim_max']:.3f} mm",
    ]
    if result["has_kerf"]:
        lines.append(f"  Kerf:       {result['kerf']:.3f} mm")
        lines.append(f"  Compensated:{result['kerf_compensated']:.3f} mm")
    if result["bend_radius"] is not None:
        lines.append(f"  Bend radius:{result['bend_radius']:.1f} mm")
    return "\n".join(lines)
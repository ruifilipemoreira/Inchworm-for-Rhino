import Rhino

RHINO_UNIT_MAP = {
    "Millimeters (mm)": Rhino.UnitSystem.Millimeters,
    "Centimeters (cm)": Rhino.UnitSystem.Centimeters,
    "Meters (m)":       Rhino.UnitSystem.Meters,
    "Inches (in)":      Rhino.UnitSystem.Inches,
    "Feet (ft)":        Rhino.UnitSystem.Feet,
}

UNIT_LABEL_MAP = {v: k for k, v in RHINO_UNIT_MAP.items()}


def get_document_unit_label():
    doc_unit = Rhino.RhinoDoc.ActiveDoc.ModelUnitSystem
    return UNIT_LABEL_MAP.get(doc_unit)


def compute_scale_factor(from_label, to_label):
    from ibis.core.units import UNITS_TO_METERS
    return UNITS_TO_METERS[from_label] / UNITS_TO_METERS[to_label]


def apply_normalization(from_label, to_label, selection_only, change_doc_units):
    doc    = Rhino.RhinoDoc.ActiveDoc
    factor = compute_scale_factor(from_label, to_label)

    if abs(factor - 1.0) < 1e-10:
        return 0, "Scale factor is 1.0 — nothing to do."

    origin    = Rhino.Geometry.Point3d.Origin
    transform = Rhino.Geometry.Transform.Scale(origin, factor)

    if selection_only:
        objects = [obj for obj in doc.Objects if obj.IsSelected(False) > 0]
    else:
        objects = list(doc.Objects)

    if not objects:
        return 0, "No objects found."

    serial = doc.BeginUndoRecord("Ibis Normalize")
    count  = sum(
        1 for obj in objects
        if doc.Objects.Transform(obj.Id, transform, True)
    )
    doc.EndUndoRecord(serial)

    if change_doc_units:
        doc.ModelUnitSystem = RHINO_UNIT_MAP[to_label]

    doc.Views.Redraw()
    return count, None
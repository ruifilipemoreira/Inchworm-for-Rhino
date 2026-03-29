import csv
import os

from ibis.core.units import UNITS_TO_METERS, format_number, extract_abbreviation


def parse_input_lines(raw_text):
    results = []
    for i, line in enumerate(raw_text.strip().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            value = float(line.replace(",", "."))
            results.append((i, value, None))
        except ValueError:
            results.append((i, None, f"Line {i}: '{line}' is not a valid number"))
    return results


def convert_batch(parsed_lines, from_unit, to_unit, scale_numerator, scale_denominator):
    from_factor = UNITS_TO_METERS[from_unit]
    to_factor   = UNITS_TO_METERS[to_unit]
    ratio       = scale_numerator / scale_denominator
    rows        = []

    for i, value, error in parsed_lines:
        if error:
            rows.append({
                "index":      i,
                "input":      "—",
                "input_unit": extract_abbreviation(from_unit),
                "output":     "ERROR",
                "output_unit": extract_abbreviation(to_unit),
                "ratio":      f"{scale_numerator}:{scale_denominator}",
                "error":      error,
            })
        else:
            value_m  = value * from_factor
            result_m = value_m * ratio
            result   = result_m / to_factor
            rows.append({
                "index":       i,
                "input":       format_number(value),
                "input_unit":  extract_abbreviation(from_unit),
                "output":      format_number(result),
                "output_unit": extract_abbreviation(to_unit),
                "ratio":       f"{scale_numerator}:{scale_denominator}",
                "error":       "",
            })
    return rows


def export_to_csv(rows, filepath):
    fieldnames = ["#", "Real", "Unit (Real)", "Model", "Unit (Model)", "Ratio", "Notes"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "#":            row["index"],
                "Real":         row["input"],
                "Unit (Real)":  row["input_unit"],
                "Model":        row["output"],
                "Unit (Model)": row["output_unit"],
                "Ratio":        row["ratio"],
                "Notes":        row["error"],
            })


def build_preview_text(rows):
    from_abbr = rows[0]["input_unit"]  if rows else ""
    to_abbr   = rows[0]["output_unit"] if rows else ""
    lines     = [f"{'#':<4} {'Real':>12} {from_abbr:<6}  {'Model':>12} {to_abbr}"]
    lines.append("─" * 46)
    for row in rows:
        if row["error"]:
            lines.append(f"{row['index']:<4} {'ERROR':>12}        {'—':>12}")
        else:
            lines.append(
                f"{row['index']:<4} {row['input']:>12} {row['input_unit']:<6}"
                f"  {row['output']:>12} {row['output_unit']}"
            )
    return "\n".join(lines)
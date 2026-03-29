import clr
clr.AddReference("Eto")
import Rhino
import Eto.Drawing as drawing
import Eto.Forms as forms

from ibis.core import tolerance as tol_core
from ibis.core.units import UNIT_KEYS, UNITS_TO_METERS, format_number, extract_abbreviation
from ibis.ui import theme
from ibis.ui.widgets import (
    make_label, make_textbox, make_dropdown, make_button,
    make_divider, make_centered_row, make_row,
)


class ToleranceTab:

    def __init__(self):
        self._build_widgets()
        self._build_page()
        self._bind_events()
        self._update_materials()
        self._recalculate()

    def _build_widgets(self):
        self.process_dd  = make_dropdown(tol_core.PROCESS_KEYS, 0, width=theme.APPLY_BTN_WIDTH)
        self.material_dd = make_dropdown([], 0, width=theme.APPLY_BTN_WIDTH)

        self.nominal_tb   = make_textbox("100", width=120)
        self.unit_dd      = make_dropdown(UNIT_KEYS, 0, width=theme.DROPDOWN_WIDTH)

        self.result_nominal    = make_label("—")
        self.result_tolerance  = make_label("—")
        self.result_min        = make_label("—")
        self.result_max        = make_label("—")
        self.result_kerf       = make_label("—")
        self.result_compensated = make_label("—")
        self.result_bend       = make_label("—")

        self.kerf_row_label        = make_label("Kerf")
        self.compensated_row_label = make_label("Kerf compensated")
        self.bend_row_label        = make_label("Min bend radius")

        self.copy_button = make_button(
            "Copy & Log  ↵",
            width=theme.APPLY_BTN_WIDTH,
            height=theme.APPLY_BTN_HEIGHT,
        )

    def _make_result_row(self, label_widget, value_widget):
        row         = forms.TableLayout()
        row.Spacing = drawing.Size(8, 0)
        row.Rows.Add(forms.TableRow(
            forms.TableCell(label_widget),
            forms.TableCell(None, True),
            forms.TableCell(value_widget),
        ))
        return row

    def _build_page(self):
        input_row = forms.TableLayout()
        input_row.Spacing = drawing.Size(6, 0)
        input_row.Rows.Add(forms.TableRow(
            forms.TableCell(self.nominal_tb),
            forms.TableCell(self.unit_dd),
            forms.TableCell(None, True),
        ))

        self._kerf_row        = self._make_result_row(self.kerf_row_label,        self.result_kerf)
        self._compensated_row = self._make_result_row(self.compensated_row_label, self.result_compensated)
        self._bend_row        = self._make_result_row(self.bend_row_label,        self.result_bend)

        rows = [
            make_label("PROCESS"),
            self.process_dd,
            make_label("MATERIAL"),
            self.material_dd,
            make_divider(),
            make_label("NOMINAL DIMENSION"),
            input_row,
            make_divider(),
            make_label("RESULTS"),
            self._make_result_row(make_label("Nominal"),   self.result_nominal),
            self._make_result_row(make_label("Tolerance"), self.result_tolerance),
            self._make_result_row(make_label("Min"),       self.result_min),
            self._make_result_row(make_label("Max"),       self.result_max),
            self._kerf_row,
            self._compensated_row,
            self._bend_row,
            make_divider(),
            make_centered_row(self.copy_button),
        ]

        layout         = forms.TableLayout()
        layout.Padding = theme.LAYOUT_PADDING
        layout.Spacing = theme.LAYOUT_SPACING
        for item in rows:
            layout.Rows.Add(forms.TableRow(forms.TableCell(item)))
        layout.Rows.Add(forms.TableRow())

        self.page         = forms.TabPage()
        self.page.Text    = "Tolerance"
        self.page.Content = layout

    def _bind_events(self):
        self.process_dd.SelectedIndexChanged  += self._on_process_changed
        self.material_dd.SelectedIndexChanged += lambda s, e: self._recalculate()
        self.nominal_tb.TextChanged           += lambda s, e: self._recalculate()
        self.unit_dd.SelectedIndexChanged     += lambda s, e: self._recalculate()
        self.copy_button.Click                += self._on_copy_clicked

    def _on_process_changed(self, sender, event):
        self._update_materials()
        self._recalculate()

    def _update_materials(self):
        process_label = self.process_dd.SelectedValue
        materials     = tol_core.get_material_keys(process_label)
        self.material_dd.DataStore     = materials
        self.material_dd.SelectedIndex = 0

    def _nominal_in_mm(self):
        unit_label    = self.unit_dd.SelectedValue
        value_in_unit = float(self.nominal_tb.Text)
        value_in_m    = value_in_unit * UNITS_TO_METERS[unit_label]
        return value_in_m * 1000.0

    def _recalculate(self):
        try:
            process_label  = self.process_dd.SelectedValue
            material_label = self.material_dd.SelectedValue
            if not material_label:
                return

            nominal_mm = self._nominal_in_mm()
            result     = tol_core.compute_tolerance_result(
                process_label, material_label, nominal_mm
            )

            unit_label = self.unit_dd.SelectedValue
            abbr       = extract_abbreviation(unit_label)
            factor     = UNITS_TO_METERS[unit_label] * 1000.0

            def to_display(mm_value):
                return f"{format_number(mm_value / factor)} {abbr}  ({format_number(mm_value)} mm)"

            self.result_nominal.Text   = to_display(result["nominal"])
            self.result_tolerance.Text = f"± {format_number(result['tolerance'])} mm"
            self.result_min.Text       = to_display(result["dim_min"])
            self.result_max.Text       = to_display(result["dim_max"])

            has_kerf    = result["has_kerf"]
            has_bend    = result["bend_radius"] is not None

            self.result_kerf.Text          = f"{format_number(result['kerf'])} mm" if has_kerf else "—"
            self.result_compensated.Text   = to_display(result["kerf_compensated"]) if has_kerf else "—"
            self.result_bend.Text          = f"{format_number(result['bend_radius'])} mm" if has_bend else "—"

            self.nominal_tb.BackgroundColor = drawing.Colors.Transparent
            self.copy_button.Enabled        = True

        except (ValueError, TypeError, KeyError, AttributeError):
            self.result_nominal.Text        = "—"
            self.result_tolerance.Text      = "—"
            self.result_min.Text            = "—"
            self.result_max.Text            = "—"
            self.result_kerf.Text           = "—"
            self.result_compensated.Text    = "—"
            self.result_bend.Text           = "—"
            self.nominal_tb.BackgroundColor = theme.COLOR_INVALID
            self.copy_button.Enabled        = False

    def _on_copy_clicked(self, sender, event):
        try:
            process_label  = self.process_dd.SelectedValue
            material_label = self.material_dd.SelectedValue
            nominal_mm     = self._nominal_in_mm()
            result         = tol_core.compute_tolerance_result(
                process_label, material_label, nominal_mm
            )
            log_text = tol_core.format_result_for_log(process_label, material_label, result)
            Rhino.RhinoApp.WriteLine(log_text)
            forms.Clipboard().Text = log_text
        except Exception:
            pass

    def handle_key_enter(self):
        if self.copy_button.Enabled:
            self._on_copy_clicked(None, None)
import clr
clr.AddReference("Eto")
import os
import Rhino
import Eto.Drawing as drawing
import Eto.Forms as forms

from ibis.core import export as export_core
from ibis.core import settings as settings_module
from ibis.core.units import UNIT_KEYS
from ibis.ui import theme
from ibis.ui.widgets import (
    make_label, make_textbox, make_dropdown, make_button,
    make_divider, make_centered_row, make_row,
)

PRESET_SCALES = ["1:20", "1:50", "1:100", "1:200", "1:500", "1:1000"]


class ExportTab:

    def __init__(self, app_settings: dict):
        self._settings    = app_settings
        self._parsed      = []
        self._rows        = []

        self._build_widgets()
        self._build_page()
        self._bind_events()

    def _build_widgets(self):
        self.scale_numerator_tb   = make_textbox(
            self._settings.get("scale_numerator",   "1"),   width=theme.RATIO_TB_WIDTH
        )
        self.scale_denominator_tb = make_textbox(
            self._settings.get("scale_denominator", "100"), width=theme.RATIO_TB_WIDTH
        )

        self.preset_buttons = []
        for preset in PRESET_SCALES:
            btn       = make_button(preset, width=theme.PRESET_BTN_WIDTH, height=theme.PRESET_BTN_HEIGHT)
            btn.Tag   = preset
            btn.Click += self._on_preset_clicked
            self.preset_buttons.append(btn)

        self.from_unit_dd = make_dropdown(UNIT_KEYS, 2, width=theme.DROPDOWN_WIDTH)
        self.to_unit_dd   = make_dropdown(UNIT_KEYS, 0, width=theme.DROPDOWN_WIDTH)

        self.input_area             = forms.TextArea()
        self.input_area.Height      = 110
        self.input_area.PlaceholderText = (
            "One dimension per line:\n10.5\n3.2\n7\n..."
        )

        self.preview_area            = forms.TextArea()
        self.preview_area.Height     = 110
        self.preview_area.ReadOnly   = True

        self.convert_button = make_button(
            "Convert",
            width=theme.APPLY_BTN_WIDTH,
            height=theme.APPLY_BTN_HEIGHT,
        )

        self.export_button = make_button(
            "Export CSV",
            width=theme.APPLY_BTN_WIDTH,
            height=theme.APPLY_BTN_HEIGHT,
        )
        self.export_button.Enabled = False

        self.status_label = make_label("")

    def _build_preset_stack(self):
        stack             = forms.StackLayout()
        stack.Orientation = forms.Orientation.Horizontal
        stack.Spacing     = 5
        for btn in self.preset_buttons:
            stack.Items.Add(forms.StackLayoutItem(btn))
        return stack

    def _build_page(self):
        ratio_row = make_row(
            self.scale_numerator_tb,
            make_label("  :  "),
            self.scale_denominator_tb,
        )

        unit_row         = forms.TableLayout()
        unit_row.Spacing = drawing.Size(8, 0)
        unit_row.Rows.Add(forms.TableRow(
            forms.TableCell(self.from_unit_dd),
            forms.TableCell(make_label("  →  ")),
            forms.TableCell(self.to_unit_dd),
            forms.TableCell(None, True),
        ))

        rows = [
            make_label("RATIO"),
            ratio_row,
            self._build_preset_stack(),
            make_divider(),
            make_label("UNITS"),
            unit_row,
            make_divider(),
            make_label("INPUT  —  one value per line"),
            self.input_area,
            make_centered_row(self.convert_button),
            make_divider(),
            make_label("PREVIEW"),
            self.preview_area,
            make_centered_row(self.export_button),
            make_centered_row(self.status_label),
        ]

        layout         = forms.TableLayout()
        layout.Padding = theme.LAYOUT_PADDING
        layout.Spacing = theme.LAYOUT_SPACING
        for item in rows:
            layout.Rows.Add(forms.TableRow(forms.TableCell(item)))
        layout.Rows.Add(forms.TableRow())

        self.page         = forms.TabPage()
        self.page.Text    = "Export"
        self.page.Content = layout

    def _bind_events(self):
        self.convert_button.Click += self._on_convert_clicked
        self.export_button.Click  += self._on_export_clicked

    def _on_preset_clicked(self, sender, event):
        parts = sender.Tag.split(":")
        self.scale_numerator_tb.Text   = parts[0].strip()
        self.scale_denominator_tb.Text = parts[1].strip()

    def _parse_ratio(self):
        n = float(self.scale_numerator_tb.Text)
        d = float(self.scale_denominator_tb.Text)
        if n == 0 or d == 0:
            raise ValueError("Ratio parts must be non-zero.")
        return n, d

    def _on_convert_clicked(self, sender, event):
        try:
            numerator, denominator = self._parse_ratio()
        except ValueError:
            self.status_label.Text     = "✗  Invalid ratio."
            self.export_button.Enabled = False
            return

        raw_text = self.input_area.Text or ""
        if not raw_text.strip():
            self.status_label.Text     = "✗  No input values."
            self.export_button.Enabled = False
            return

        self._parsed = export_core.parse_input_lines(raw_text)
        self._rows   = export_core.convert_batch(
            self._parsed,
            self.from_unit_dd.SelectedValue,
            self.to_unit_dd.SelectedValue,
            numerator,
            denominator,
        )

        self.preview_area.Text = export_core.build_preview_text(self._rows)

        errors = sum(1 for r in self._rows if r["error"])
        total  = len(self._rows)

        if errors == 0:
            self.status_label.Text = f"✓  {total} values converted."
        else:
            self.status_label.Text = f"⚠  {total - errors} converted, {errors} errors."

        self.export_button.Enabled = total > errors

    def _on_export_clicked(self, sender, event):
        if not self._rows:
            return

        dialog            = forms.SaveFileDialog()
        dialog.Title      = "Export CSV"
        dialog.Filters.Add(forms.FileFilter("CSV files", ".csv"))
        dialog.FileName   = "ibis_export.csv"

        if dialog.ShowDialog(None) != forms.DialogResult.Ok:
            return

        filepath = dialog.FileName
        try:
            export_core.export_to_csv(self._rows, filepath)
            Rhino.RhinoApp.WriteLine(f"Ibis Export: saved {len(self._rows)} rows to {filepath}")
            self.status_label.Text = f"✓  Saved to {os.path.basename(filepath)}"
        except OSError as e:
            self.status_label.Text = f"✗  {e}"

    def handle_key_enter(self):
        self._on_convert_clicked(None, None)
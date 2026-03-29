import clr
clr.AddReference("Eto")
import Eto.Drawing as drawing
import Eto.Forms as forms

from ibis.core import normalize as norm_core
from ibis.core.units import UNIT_KEYS, format_number, extract_abbreviation
from ibis.ui import theme
from ibis.ui.widgets import (
    make_label, make_dropdown, make_button,
    make_divider, make_centered_row, make_row,
)


class NormalizeTab:

    def __init__(self):
        self._build_widgets()
        self._build_page()
        self._bind_events()
        self._refresh_doc_units()

    def _build_widgets(self):
        self.doc_units_label = make_label("—")
        self.refresh_button  = make_button("↻", width=28, height=24)

        self.from_dd = make_dropdown(UNIT_KEYS, 0, width=theme.DROPDOWN_WIDTH)
        self.to_dd   = make_dropdown(UNIT_KEYS, 2, width=theme.DROPDOWN_WIDTH)

        self.factor_label = make_label("Scale factor: —")

        self.scope_all_rb = forms.RadioButton()
        self.scope_all_rb.Text = "All objects in document"
        self.scope_all_rb.Checked = True

        self.scope_sel_rb = forms.RadioButton(self.scope_all_rb)
        self.scope_sel_rb.Text = "Selected objects only"

        self.change_units_cb         = forms.CheckBox()
        self.change_units_cb.Text    = "Change document units to target"
        self.change_units_cb.Checked = True

        self.apply_button = make_button(
            "Apply Normalization",
            width=theme.APPLY_BTN_WIDTH,
            height=theme.APPLY_BTN_HEIGHT,
        )

        self.status_label = make_label("")

    def _build_page(self):
        doc_row         = forms.TableLayout()
        doc_row.Spacing = drawing.Size(6, 0)
        doc_row.Rows.Add(forms.TableRow(
            forms.TableCell(self.doc_units_label, True),
            forms.TableCell(self.refresh_button),
        ))

        unit_row         = forms.TableLayout()
        unit_row.Spacing = drawing.Size(8, 0)
        unit_row.Rows.Add(forms.TableRow(
            forms.TableCell(self.from_dd),
            forms.TableCell(make_label("  →  ")),
            forms.TableCell(self.to_dd),
            forms.TableCell(None, True),
        ))

        scope_stack = forms.StackLayout()
        scope_stack.Orientation = forms.Orientation.Vertical
        scope_stack.Spacing = 4
        scope_stack.Items.Add(forms.StackLayoutItem(self.scope_all_rb))
        scope_stack.Items.Add(forms.StackLayoutItem(self.scope_sel_rb))

        rows = [
            make_label("DOCUMENT UNITS"),
            doc_row,
            make_divider(),
            make_label("RESCALE"),
            unit_row,
            make_centered_row(self.factor_label),
            make_divider(),
            make_label("SCOPE"),
            scope_stack,
            self.change_units_cb,
            make_divider(),
            make_centered_row(self.apply_button),
            make_centered_row(self.status_label),
        ]

        layout         = forms.TableLayout()
        layout.Padding = theme.LAYOUT_PADDING
        layout.Spacing = theme.LAYOUT_SPACING
        for item in rows:
            layout.Rows.Add(forms.TableRow(forms.TableCell(item)))
        layout.Rows.Add(forms.TableRow())

        self.page         = forms.TabPage()
        self.page.Text    = "Normalize"
        self.page.Content = layout

    def _bind_events(self):
        self.refresh_button.Click         += lambda s, e: self._refresh_doc_units()
        self.from_dd.SelectedIndexChanged += lambda s, e: self._update_factor()
        self.to_dd.SelectedIndexChanged   += lambda s, e: self._update_factor()
        self.apply_button.Click           += self._on_apply_clicked

    def _refresh_doc_units(self):
        label = norm_core.get_document_unit_label()
        if label:
            self.doc_units_label.Text  = label
            self.from_dd.SelectedIndex = UNIT_KEYS.index(label)
        else:
            self.doc_units_label.Text = "Unsupported unit system"
        self._update_factor()
        self.status_label.Text = ""

    def _update_factor(self):
        try:
            from_label = self.from_dd.SelectedValue
            to_label   = self.to_dd.SelectedValue
            factor     = norm_core.compute_scale_factor(from_label, to_label)
            self.factor_label.Text    = f"Scale factor: × {format_number(factor)}"
            self.apply_button.Enabled = abs(factor - 1.0) > 1e-10
        except Exception:
            self.factor_label.Text    = "Scale factor: —"
            self.apply_button.Enabled = False

    def _on_apply_clicked(self, sender, event):
        from_label     = self.from_dd.SelectedValue
        to_label       = self.to_dd.SelectedValue
        selection_only = self.scope_sel_rb.Checked
        change_units   = self.change_units_cb.Checked == True

        count, error = norm_core.apply_normalization(
            from_label, to_label, selection_only, change_units
        )

        if error:
            self.status_label.Text = f"✗  {error}"
        else:
            from_abbr = extract_abbreviation(from_label)
            to_abbr   = extract_abbreviation(to_label)
            self.status_label.Text = (
                f"✓  {count} objects rescaled  {from_abbr} → {to_abbr}"
            )
            self._refresh_doc_units()

    def handle_key_enter(self):
        if self.apply_button.Enabled:
            self._on_apply_clicked(None, None)
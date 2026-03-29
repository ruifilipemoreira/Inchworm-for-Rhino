import clr
clr.AddReference("Eto")
import Rhino
import Eto.Drawing as drawing
import Eto.Forms as forms

from ibis.core import units, settings as settings_module
from ibis.core.history import SessionHistory
from ibis.ui import theme
from ibis.ui.widgets import (
    make_label, make_textbox, make_dropdown, make_button,
    make_divider, make_row, make_centered_row,
)


class ScaleTab:

    def __init__(self, history: SessionHistory, app_settings: dict):
        self._history     = history
        self._settings    = app_settings
        self.is_updating  = False
        self.final_output = None

        self._build_widgets()
        self._build_page()
        self._bind_events()
        self._recalculate(from_real=True)

    def _build_widgets(self):
        self.scale_numerator_tb   = make_textbox(
            self._settings["scale_numerator"],   width=theme.RATIO_TB_WIDTH
        )
        self.scale_denominator_tb = make_textbox(
            self._settings["scale_denominator"], width=theme.RATIO_TB_WIDTH
        )

        self.preset_buttons = []
        for preset in units.PRESET_SCALES:
            btn       = make_button(preset, width=theme.PRESET_BTN_WIDTH, height=theme.PRESET_BTN_HEIGHT)
            btn.Tag   = preset
            btn.Click += self._on_preset_clicked
            self.preset_buttons.append(btn)

        self.direction_label = make_label("▼  Real → Model")

        self.real_length_tb  = make_textbox("0", width=theme.CONVERSION_TB_WIDTH)
        self.model_length_tb = make_textbox("0", width=theme.CONVERSION_TB_WIDTH)
        self.real_unit_dd    = make_dropdown(
            units.UNIT_KEYS, self._settings["real_unit_index"],  width=theme.DROPDOWN_WIDTH
        )
        self.model_unit_dd   = make_dropdown(
            units.UNIT_KEYS, self._settings["model_unit_index"], width=theme.DROPDOWN_WIDTH
        )

        self.swap_button = make_button(
            "⇅  Swap", width=theme.SWAP_BTN_WIDTH, height=theme.SWAP_BTN_HEIGHT
        )

        self.output_label               = forms.Label()
        self.output_label.Text          = "—"
        self.output_label.VerticalAlignment = forms.VerticalAlignment.Center

        self.copy_button = make_button(
            "Copy  ↵", width=theme.COPY_BTN_WIDTH, height=theme.COPY_BTN_HEIGHT
        )

        self.history_listbox        = forms.ListBox()
        self.history_listbox.Height = theme.HISTORY_HEIGHT

    def _build_preset_stack(self):
        stack             = forms.StackLayout()
        stack.Orientation = forms.Orientation.Horizontal
        stack.Spacing     = 5
        for btn in self.preset_buttons:
            stack.Items.Add(forms.StackLayoutItem(btn))
        return stack

    def _build_page(self):
        result_row         = forms.TableLayout()
        result_row.Spacing = drawing.Size(8, 0)
        result_row.Rows.Add(forms.TableRow(
            forms.TableCell(self.output_label, True),
            forms.TableCell(self.copy_button),
        ))

        rows = [
            make_label("RATIO"),
            make_row(self.scale_numerator_tb, make_label("  :  "), self.scale_denominator_tb),
            self._build_preset_stack(),
            make_divider(),
            self.direction_label,
            make_row(self.real_length_tb,  self.real_unit_dd),
            make_centered_row(self.swap_button),
            make_row(self.model_length_tb, self.model_unit_dd),
            make_divider(),
            result_row,
            make_divider(),
            make_label("RECENT"),
            self.history_listbox,
        ]

        layout         = forms.TableLayout()
        layout.Padding = theme.LAYOUT_PADDING
        layout.Spacing = theme.LAYOUT_SPACING
        for item in rows:
            layout.Rows.Add(forms.TableRow(forms.TableCell(item)))
        layout.Rows.Add(forms.TableRow())

        self.page         = forms.TabPage()
        self.page.Text    = "Scale"
        self.page.Content = layout

    def _bind_events(self):
        self.scale_numerator_tb.TextChanged     += lambda s, e: self._recalculate(from_real=True)
        self.scale_denominator_tb.TextChanged   += lambda s, e: self._recalculate(from_real=True)
        self.real_length_tb.TextChanged         += lambda s, e: self._recalculate(from_real=True)
        self.real_unit_dd.SelectedIndexChanged  += lambda s, e: self._recalculate(from_real=True)
        self.model_length_tb.TextChanged        += lambda s, e: self._recalculate(from_real=False)
        self.model_unit_dd.SelectedIndexChanged += lambda s, e: self._recalculate(from_real=True)
        self.swap_button.Click                  += self._on_swap_clicked
        self.copy_button.Click                  += self._on_copy_clicked

    def collect_settings(self):
        return {
            "scale_numerator":   self.scale_numerator_tb.Text,
            "scale_denominator": self.scale_denominator_tb.Text,
            "real_unit_index":   self.real_unit_dd.SelectedIndex,
            "model_unit_index":  self.model_unit_dd.SelectedIndex,
        }

    def handle_key_enter(self):
        self._on_copy_clicked(None, None)

    def _parse_ratio(self):
        n = float(self.scale_numerator_tb.Text)
        d = float(self.scale_denominator_tb.Text)
        if n == 0 or d == 0:
            raise ValueError("Ratio parts must be non-zero.")
        return n / d

    def _set_field_valid(self, textbox, valid):
        textbox.BackgroundColor = (
            drawing.Colors.Transparent if valid else theme.COLOR_INVALID
        )

    def _update_direction_indicator(self, from_real):
        self.direction_label.Text = (
            "▼  Real → Model" if from_real else "▲  Model → Real"
        )

    def _recalculate(self, from_real):
        if self.is_updating:
            return
        self.is_updating = True
        self._update_direction_indicator(from_real)
        active_field = self.real_length_tb if from_real else self.model_length_tb
        try:
            ratio = self._parse_ratio()
            if from_real:
                real_m = units.to_meters(
                    self.real_length_tb.Text, self.real_unit_dd.SelectedValue
                )
                self.model_length_tb.Text = units.format_number(
                    units.from_meters(real_m * ratio, self.model_unit_dd.SelectedValue)
                )
            else:
                model_m = units.to_meters(
                    self.model_length_tb.Text, self.model_unit_dd.SelectedValue
                )
                self.real_length_tb.Text = units.format_number(
                    units.from_meters(model_m / ratio, self.real_unit_dd.SelectedValue)
                )
            self._set_field_valid(active_field, valid=True)
        except ValueError:
            self._set_field_valid(active_field, valid=False)
        self._refresh_output_label()
        self.is_updating = False

    def _refresh_output_label(self):
        try:
            real_val   = units.format_number(float(self.real_length_tb.Text))
            model_val  = units.format_number(float(self.model_length_tb.Text))
            real_unit  = units.extract_abbreviation(self.real_unit_dd.SelectedValue)
            model_unit = units.extract_abbreviation(self.model_unit_dd.SelectedValue)
            num = self.scale_numerator_tb.Text
            den = self.scale_denominator_tb.Text
            self.output_label.Text = (
                f"{num}:{den}  ·  {real_val} {real_unit} → {model_val} {model_unit}"
            )
        except (ValueError, TypeError):
            self.output_label.Text = "—"

    def _on_preset_clicked(self, sender, event):
        parts = sender.Tag.split(":")
        self.is_updating = True
        self.scale_numerator_tb.Text   = parts[0].strip()
        self.scale_denominator_tb.Text = parts[1].strip()
        self.is_updating = False
        self._recalculate(from_real=True)

    def _on_swap_clicked(self, sender, event):
        real_text  = self.real_length_tb.Text
        model_text = self.model_length_tb.Text
        real_idx   = self.real_unit_dd.SelectedIndex
        model_idx  = self.model_unit_dd.SelectedIndex
        self.is_updating = True
        self.real_length_tb.Text         = model_text
        self.model_length_tb.Text        = real_text
        self.real_unit_dd.SelectedIndex  = model_idx
        self.model_unit_dd.SelectedIndex = real_idx
        self.is_updating = False
        self._recalculate(from_real=True)

    def _on_copy_clicked(self, sender, event):
        output = self.output_label.Text
        if output == "—":
            return
        self.final_output = output
        self._history.add(output)
        self.history_listbox.DataStore = self._history.entries
        settings_module.save(self.collect_settings())
        Rhino.RhinoApp.WriteLine(f"Ibis: {output}")
        forms.Clipboard().Text = output
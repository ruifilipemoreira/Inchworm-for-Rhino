import clr
clr.AddReference("Eto")
import Eto.Drawing as drawing
import Eto.Forms as forms


def make_label(text):
    label = forms.Label()
    label.Text = text
    label.VerticalAlignment = forms.VerticalAlignment.Center
    return label


def make_textbox(text, width=None):
    tb = forms.TextBox()
    tb.Text = text
    if width is not None:
        tb.Width = width
    return tb


def make_dropdown(items, index, width=155):
    dd = forms.DropDown()
    dd.DataStore = items
    dd.SelectedIndex = index
    dd.Width = width
    return dd


def make_button(text, width=None, height=None):
    btn = forms.Button()
    btn.Text = text
    if width:
        btn.Width = width
    if height:
        btn.Height = height
    return btn


def make_divider():
    panel = forms.Panel()
    panel.Height = 1
    return panel


def make_row(*controls, spacing=6):
    row = forms.TableLayout()
    row.Spacing = drawing.Size(spacing, 0)
    row.Rows.Add(forms.TableRow(*[forms.TableCell(c) for c in controls]))
    return row


def make_centered_row(control):
    row = forms.TableLayout()
    row.Rows.Add(forms.TableRow(
        forms.TableCell(None, True),
        forms.TableCell(control),
        forms.TableCell(None, True),
    ))
    return row
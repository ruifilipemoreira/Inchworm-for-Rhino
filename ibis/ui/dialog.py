import clr
clr.AddReference("Eto")
import Eto.Drawing as drawing
import Eto.Forms as forms

from ibis.core import settings as settings_module
from ibis.core.history import SessionHistory
from ibis.ui import theme
from ibis.ui.tabs.scale     import ScaleTab
from ibis.ui.tabs.normalize import NormalizeTab
from ibis.ui.tabs.tolerance import ToleranceTab
from ibis.ui.tabs.export    import ExportTab


class IbisDialog(forms.Form):

    def __init__(self):
        super().__init__()
        self.Title     = "Ibis"
        self.Resizable = False
        self.Topmost   = True

        self._history  = SessionHistory()
        self._settings = settings_module.load()

        self._build_tabs()
        self._build_layout()
        self._bind_events()
        self._resize_for_tab(0)

    def _build_tabs(self):
        self._scale_tab     = ScaleTab(self._history, self._settings)
        self._normalize_tab = NormalizeTab()
        self._tolerance_tab = ToleranceTab()
        self._export_tab    = ExportTab(self._settings)

    def _build_layout(self):
        self._tab_control = forms.TabControl()
        self._tab_control.Pages.Add(self._scale_tab.page)
        self._tab_control.Pages.Add(self._normalize_tab.page)
        self._tab_control.Pages.Add(self._tolerance_tab.page)
        self._tab_control.Pages.Add(self._export_tab.page)
        self.Content = self._tab_control

    def _bind_events(self):
        self._tab_control.SelectedIndexChanged += lambda s, e: self._on_tab_changed()
        self.KeyDown                           += self._on_key_down

    def _on_tab_changed(self):
        index = self._tab_control.SelectedIndex
        self._resize_for_tab(index)
        if index == 1:
            self._normalize_tab._refresh_doc_units()

    def _resize_for_tab(self, index):
        self.ClientSize = drawing.Size(
            theme.WINDOW_WIDTH,
            theme.TAB_HEIGHTS.get(index, 200),
        )

    def _on_key_down(self, sender, e):
        if str(e.Key) != "Enter":
            return
        index = self._tab_control.SelectedIndex
        if index == 0:
            self._scale_tab.handle_key_enter()
        elif index == 1:
            self._normalize_tab.handle_key_enter()
        elif index == 2:
            self._tolerance_tab.handle_key_enter()
        elif index == 3:
            self._export_tab.handle_key_enter()
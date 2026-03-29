import clr
clr.AddReference("Rhino.UI")

import Rhino
import Eto.Forms as forms
from ibis.ui.dialog import IbisDialog

_ibis_window = None

def run_scale_command():
    global _ibis_window
    
    if _ibis_window is not None and not _ibis_window.IsDisposed:
        _ibis_window.BringToFront()
        return

    _ibis_window = IbisDialog()
    _ibis_window.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    _ibis_window.Show()
import clr
clr.AddReference("Eto")
import Eto.Drawing as drawing

WINDOW_WIDTH = 420

TAB_HEIGHTS = {
    0: 490,
    1: 390,
    2: 500,
    3: 600,
}

COLOR_INVALID       = drawing.Color.FromArgb(255, 100, 100)
LAYOUT_PADDING      = drawing.Padding(16, 14, 16, 14)
LAYOUT_SPACING      = drawing.Size(6, 8)

DROPDOWN_WIDTH      = 155
CONVERSION_TB_WIDTH = 220
RATIO_TB_WIDTH      = 70
PRESET_BTN_WIDTH    = 58
PRESET_BTN_HEIGHT   = 24
SWAP_BTN_WIDTH      = 90
SWAP_BTN_HEIGHT     = 26
COPY_BTN_WIDTH      = 90
COPY_BTN_HEIGHT     = 28
HISTORY_HEIGHT      = 90
APPLY_BTN_WIDTH     = 380
APPLY_BTN_HEIGHT    = 32
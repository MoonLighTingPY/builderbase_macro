from PyQt5 import QtWidgets, QtCore, QtGui
import sys

class OverlayStatus(QtWidgets.QWidget):
    COLORS = {
        "yellow": "#FFFF00",
        "orange": "#FFA500",
        "red": "#FF0000",
        "green": "#00FF00",
        "purple": "#CA00CA",
        "default": "#222222"
    }
    ALPHA = 0.9

    def __init__(self, width=220, height=38):
        super().__init__(
            None,
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.BypassWindowManagerHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlag(QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setWindowFlag(QtCore.Qt.WindowTransparentForInput, True)  # Click-through
        self.resize(width, height)
        self.text = ""
        self.color = "default"
        self.hide()

    def _set_position(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 10  # 10 pixels from right
        y = screen.height() - self.height() - 50  # 10 pixels from bottom
        self.move(x, y)

    def show(self, text, color="default"):
        self.text = text
        self.color = color
        self._set_position()
        super().show()
        self.update()

    def hide(self):
        super().hide()

    def destroy(self):
        self.close()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        color = QtGui.QColor(self.COLORS.get(self.color, self.COLORS["default"]))
        color.setAlphaF(self.ALPHA)
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        painter.setPen(QtGui.QColor("#fff"))
        font = painter.font()
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.text)

_overlay_instance = None

def get_overlay():
    global _overlay_instance
    if _overlay_instance is None:
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        _overlay_instance = OverlayStatus()
    return _overlay_instance

def update_overlay_status(text, color="default", root=None):
    overlay = get_overlay()
    overlay.show(text, color)

def hide_overlay_status():
    overlay = get_overlay()
    overlay.hide()

def destroy_overlay_status():
    overlay = get_overlay()
    overlay.destroy()
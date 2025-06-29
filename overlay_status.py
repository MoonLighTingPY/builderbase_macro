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

        # Calculate luminance to determine if background is bright
        r, g, b = color.red(), color.green(), color.blue()
        luminance = 0.299 * r + 0.587 * g + 0.114 * b

        font = painter.font()
        font.setPointSize(14)
        painter.setFont(font)

        rect = self.rect()
        text = self.text

        if luminance > 100:
            # Bright background: draw black outline, then white text
            painter.setPen(QtGui.QColor("#000"))
            # Draw text outline by offsetting in 8 directions
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        painter.drawText(rect.translated(dx, dy), QtCore.Qt.AlignCenter, text)
            painter.setPen(QtGui.QColor("#fff"))
            painter.drawText(rect, QtCore.Qt.AlignCenter, text)
        else:
            # Dark background: just white text
            painter.setPen(QtGui.QColor("#fff"))
            painter.drawText(rect, QtCore.Qt.AlignCenter, text)

_overlay_instance = None
_overlay_app = None

def get_overlay():
    global _overlay_instance, _overlay_app
    if _overlay_instance is None:
        _overlay_app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
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

def overlay_status_listener(queue):
    """
    Listens for overlay status commands from the queue and updates the overlay accordingly.
    This function must be called from the main thread of the main process.
    It will start the Qt event loop if not already running.
    """
    overlay = get_overlay()

    def process_queue():
        while not queue.empty():
            try:
                msg = queue.get_nowait()
                if not msg:
                    continue
                cmd = msg[0]
                if cmd == "show":
                    text = msg[1] if len(msg) > 1 else ""
                    color = msg[2] if len(msg) > 2 else "default"
                    overlay.show(text, color)
                elif cmd == "hide":
                    overlay.hide()
                elif cmd == "destroy":
                    overlay.destroy()
            except Exception as e:
                print(f"OverlayStatusListener error: {e}")

    timer = QtCore.QTimer()
    timer.timeout.connect(process_queue)
    timer.start(100)  # Check the queue every 100ms

    _overlay_app.exec_()
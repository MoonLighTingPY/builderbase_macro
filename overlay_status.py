import tkinter as tk
import threading

class OverlayStatus:
    COLORS = {
        "yellow": "#FFFF00",
        "orange": "#FFA500",
        "red": "#FF0000",
        "green": "#00FF00",
        "default": "#222222"
    }
    ALPHA = 0.75

    def __init__(self, root, width=220, height=38):
        self.overlay = tk.Toplevel(root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", self.ALPHA)
        self.overlay.configure(bg=self.COLORS["default"])
        self.width = width
        self.height = height
        self._set_position()
        self.overlay.withdraw()
        self.lock = threading.Lock()

        # Use Canvas for text with outline
        self.canvas = tk.Canvas(self.overlay, width=self.width, height=self.height, highlightthickness=0, bg=self.COLORS["default"])
        self.canvas.pack(fill="both", expand=True)
        self.text_id = None
        self.current_bg = self.COLORS["default"]

    def _set_position(self):
        self.overlay.update_idletasks()
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()
        x = screen_width - self.width - 5
        y = screen_height - self.height - 5
        self.overlay.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def _draw_text_with_outline(self, text, fg, bg):
        self.canvas.delete("all")
        font = ("Segoe UI", 11, "bold")
        x = self.width // 2
        y = self.height // 2
        outline_color = "black"
        # Draw outline by drawing text in 8 directions
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
            self.canvas.create_text(x+dx, y+dy, text=text, font=font, fill=outline_color)
        # Draw main text
        self.canvas.create_text(x, y, text=text, font=font, fill=fg)

    def show(self, text, color="default"):
        with self.lock:
            bg = self.COLORS.get(color, self.COLORS["default"])
            fg = "white" if color != "yellow" else "#222222"  # Use dark text for yellow bg
            self.current_bg = bg
            self.overlay.configure(bg=bg)
            self.canvas.configure(bg=bg)
            self._set_position()
            self._draw_text_with_outline(text, fg, bg)
            self.overlay.deiconify()
            self.overlay.attributes("-topmost", True)
            # Return focus to the main window to prevent minimizing
            if hasattr(self.overlay, 'master') and self.overlay.master is not None:
                try:
                    self.overlay.master.focus_force()
                except Exception:
                    pass

    def hide(self):
        with self.lock:
            self.overlay.withdraw()

    def destroy(self):
        with self.lock:
            try:
                self.overlay.destroy()
            except Exception:
                pass

_overlay_instance = None

def get_overlay(root=None):
    global _overlay_instance
    if _overlay_instance is None:
        if root is None:
            raise RuntimeError("OverlayStatus requires a Tk root window")
        _overlay_instance = OverlayStatus(root)
    return _overlay_instance

def update_overlay_status(text, color="default", root=None):
    get_overlay(root).show(text, color)

def hide_overlay_status(root=None):
    get_overlay(root).hide()

def destroy_overlay_status():
    global _overlay_instance
    if _overlay_instance is not None:
        _overlay_instance.destroy()
        _overlay_instance = None
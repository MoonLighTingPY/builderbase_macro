class OverlayStatus:
    COLORS = {
        "yellow": "#FFFF00",
        "orange": "#FFA500",
        "red": "#FF0000",
        "green": "#00FF00",
        "purple": "#CA00CA",
        "default": "#222222"
    }
    ALPHA = 0.75

    def __init__(self, width=220, height=38):
        pass


    def _set_position(self):
        pass


    def show(self, text, color="default"):
        pass


    def hide(self):
        pass

    def destroy(self):
        pass


def get_overlay():
    pass

def update_overlay_status(text, color="default", root=None):
    pass

def hide_overlay_status():
    pass

def destroy_overlay_status():
    pass
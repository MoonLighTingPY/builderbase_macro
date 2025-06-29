import multiprocessing

class OverlayStatusProxy:
    def __init__(self, manager=None):
        if manager is None:
            manager = multiprocessing.Manager()
        self.manager = manager
        self.queue = self.manager.Queue()

    def get_queue(self):
        return self.queue

    def show(self, text, color="default"):
        self.queue.put(("show", text, color))

    def hide(self):
        self.queue.put(("hide",))

    def destroy(self):
        self.queue.put(("destroy",))
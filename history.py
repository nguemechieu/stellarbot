from tkinter import Frame


class History(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.init_ui()

    def init_ui(self):

        self.parent.title("History")
        self.pack()
        pass
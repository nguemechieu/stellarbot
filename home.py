from tkinter import Frame, BOTH, Label


class Home(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.Label1 = None
        self.controller = controller
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.Label1 = Label(self, text="Home")
        self.Label1.pack()
        self.Label1.bind("<Button-1>", lambda e: self.controller.show_frame("Login"))

        self.pack(fill=BOTH, expand=1)

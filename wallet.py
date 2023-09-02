from tkinter import Frame


class Wallet(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.parent.title("Wallet")
        self.parent.geometry("1000x600")

from tkinter import Frame


class OrderBook(Frame):

    def  __init__(self, parent=None, controller=None):

        self.parent=parent
        self.controller=controller
        Frame.__init__(self, parent)
        
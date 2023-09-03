from tkinter import N,S,W,E, Frame, Label


class Orders(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.grid()
        self.createWidgets()
    
    def createWidgets(self):


        self.label = Label(self, text="Orders")
        self.label.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W)
from tkinter import Button, Entry, Frame, Label


class CreateAccount(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.grid( row=0, column=0, columnspan=2, sticky="nsew")
        
        self.login_button = Button(self, text="GO BACK", command=lambda:self.controller.show_pages("Login"))
        self.login_button.grid( row=3, column=2, padx=1)
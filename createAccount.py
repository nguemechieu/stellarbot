from tkinter import Button, Entry, Frame, Label


class CreateAccount(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
   
        self.create_account_label = Label(self, text="Create Account",  fg="black", font=("Arial", 20))
        self.create_account_label.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        

        self.username_label = Label(self, text="Username",  fg="black", font=("Arial", 10))
        self.username_label.grid(row=2, column=3, columnspan=2, sticky="nsew")
       



        self.create_account_button = Button(self, text="Create Account",command=lambda:None, bg="white", fg="black", font=("Arial", 10))
        self.create_account_button.grid( row=3, column=0, columnspan=2, sticky="nsew",padx=200,pady=100)

        self.login_button = Button(self, text="GO BACK", command=lambda:self.controller.show_pages("Login"),padx=200,pady=100)
        self.login_button.grid( row=3, column=2)

        self.grid( row=0, column=0, columnspan=2, sticky="nsew")
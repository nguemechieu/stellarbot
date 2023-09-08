from tkinter import Button, Entry, Frame, Label


class CreateAccount(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        self.parent.title("Create Account")
    

        self.create_account_label = Label(self.parent, text="Create Account", bg="white", fg="black", font=("Arial", 20))
        
        self.create_account_label.configure(activebackground="white")

        self.username_label = Label(self.parent, text="Username", bg="white", fg="black", font=("Arial", 10))
        self.username_label.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.username_label.configure(activebackground="white")



        self.create_account_button = Button(self.parent, text="Create Account", bg="white", fg="black", font=("Arial", 10))
        self.create_account_button.pack(pady=10, padx=10)

        self.login_button = Button(self.parent, text="Login", bg="white", fg="black", font=("Arial", 10), command=self.controller.show_page("Login"))
        self.login_button.grid( row=6, column=1)
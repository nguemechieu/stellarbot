from tkinter import Button, Entry, Frame, Label
import tkinter


class CreateAccount(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.grid( row=0, column=0, columnspan=2, sticky="nsew")

        self.label=Label(self,text='CREATE ACCOUNT ')
        self.label.pack(side=tkinter.TOP, fill=tkinter.X)
      

        self.text= tkinter.Text( bg='black',border=2, width=300, height=1)
        self.text.grid(row=4,column=0,padx=30,pady=100)
        self.text.insert(tkinter.END, "Enter your username and password")
     
        
        self.login_button = Button(self, text="GO BACK", command=lambda:self.controller.show_pages("Login"))
        self.login_button.place(x=100, y=100)


        self.create_btn =Button(self,text='Click Here to Create Account!')
        self.create_btn.place(x=100, y=300)

        self.config(bg='green',relief='ridge',width=1530, height=800)


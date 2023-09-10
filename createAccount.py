from tkinter import Button, Entry, Frame, Label
import tkinter


class CreateAccount(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.grid( row=0, column=0, columnspan=2, sticky="nsew")

        self.label=Label(self,text='CREATE ACCOUNT ')
        self.label.grid(row=1,column=1)
      

        self.text= tkinter.Text( bg='black',border=2)
        self.text.grid(row=4,column=0,padx=30,pady=100)
        self.text.config(background='black',relief='ridge',width=300)
     
        
        self.login_button = Button(self, text="GO BACK", command=lambda:self.controller.show_pages("Login"))
        self.login_button.grid( row=3, column=2, padx=10,pady=40)


        self.create_btn =Button(self,text='Click Here to Create Account!')
        self.create_btn.grid(row=3,column =4,padx=10,pady=40)


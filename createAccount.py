from tkinter import Button, Entry, Label
import tkinter


class CreateAccount(tkinter.Frame):

    def __init__(self, parent=None,controller=None):
        tkinter.Frame.__init__(self, parent)
        self.controller=controller

        self.image = tkinter.PhotoImage(file="./src/images/stellarbot.png")
        self.welcome_label = tkinter.Label(self, text="Create Stellar Lumen's Account", font=("Helvetica" ,35),bg='green',fg='white')
        self.welcome_label.place(x=0,y=0)
   
        self.account_id=tkinter.StringVar()
        self.secret_key=tkinter.StringVar()



        # Create  screen to display information
        self.screen_info_canvas = tkinter.Canvas(self, width=1530, height=600, background='black')
        self.screen_info_canvas.place(x=0,y=0)
        self.screen_info_canvas.create_text(300,100,text="Welcome to Stellarbot  ",font=("Helvetica",15),fill='white')
        self.screen_info_canvas.create_text(400,200,text="Please click buttons to create your new account! ",font=("Helvetica",15),fill='white')
        
        self.go_back_account_button = tkinter.Button(self, text="Go Back",font=("Helvetica",15), bg='gray',fg='white',command=lambda: self.controller.show_pages("Login"))   
        self.go_back_account_button.place(x=420,y=610)


        self.create_account_button = tkinter.Button(self, text="Create New Account",command=lambda:self.get_data(),font=("Helvetica",15), bg='gray',fg='white')
        self.create_account_button.place(x=520,y=610)

      
        
        self.config(bg='green', width=1530,height = 800)
        self.welcome_label.config(image=self.image,padx=0,pady=0,bg='green',fg='white',width=1530,height=800,anchor= 'n')

        self.grid(row=0,column=0,sticky= 'nsew')
    

    def get_data(self)->None:
      a,s  =self.controller.bot.create_account()
      self.account_id.set(a)
      self.secret_key.set(s)
      self.screen_info_canvas.delete('all')
      self.screen_info_canvas.create_text(300,100, text="Account ID: ",font=("Helvetica",15),fill='white')
     
      self.account_entry=tkinter.Entry(self, textvariable=self.account_id,font=("Helvetica",15),fg='green',width=400)
      self.account_entry.place(x=600,y=100)
      self.account_entry.setvar('',self.account_id)
      self.screen_info_canvas.create_text(300,200, text="Secret Key: ",font=("Helvetica",15),fill='white')

      self.secret_key_entry=tkinter.Entry(self, textvariable=self.secret_key,font=("Helvetica",15),fg='green',width=400)
      self.secret_key_entry.place(x=600,y=200)
      self.secret_key_entry.setvar('',self.secret_key)

      self.screen_info_canvas.create_text(400,500, text=self.controller.bot.server_msg['message'].__str__(),font=("Helvetica",15),fill='white')
      self.screen_info_canvas.create_text(400,550, text='Please copy and save your account id and private key.\nThen activate your account by sending some XLM  inside!\nYou can purchase it via monpay or any crypto exchanges.',font=("Helvetica",15),fill='white')
    
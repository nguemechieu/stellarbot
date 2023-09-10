import tkinter
from tkinter import IntVar, StringVar, ttk

import pandas as pd


class Login(tkinter.Frame):

    def __init__(self, parent=None,controller=None):
        tkinter.Frame.__init__(self, parent)

        self.controller=controller
        self.grid( row =0,column=0,pady=200,ipadx=900,ipady=0, sticky ='nswe')

        self.image = tkinter.PhotoImage(file="./src/images/stellarbot.png")
        self.label = tkinter.Label(self, image=self.image)
        self.welcome_label = tkinter.Label(self, text="Welcome to Stellar Bot", font=("Helvetica",25),bg='green',fg='white')
        self.welcome_label.grid(row=1,column=3,padx=20,sticky ='nswe',ipadx=10)
        self.label.place(x=100,y=200)
        self.config(bg='black',border=4,relief='ridge')
        self.account_id=StringVar()
        self.account_id.set("")
      
        self.account_secret=StringVar()
        self.account_secret.set("")
        
        
        

        tkinter.Label(self,text="Account ID",font=("Helvetica",10)).grid(row=1,column=5,pady=30,padx=50)
 
        tkinter.Entry(self,textvariable=self.account_id,font=("Arial",10)).grid(row=1,column=6,ipadx=200,pady=30)

        tkinter.Label(self,text="Account Secret",font=("Helvetica",10)).grid(row=2,column=5,pady=30,padx=50)
     
     
        tkinter.Entry(self,textvariable=self.account_secret,font=("Arial",10)).grid(row=2,column=6,pady=30,ipadx=200)
        self.remember_me=IntVar()
        self.remember_me.set(True)

        tkinter.Label(self,text="Remember Me",font=("Helvetica",10)).grid(row=5,column=5,pady=30,padx=50)
        
        tkinter.Checkbutton(self,textvariable=self.remember_me,font=("Arial",10)).grid(row=5,column=6,pady=30,padx=50)

        tkinter.Button(self,text="Login",command=lambda:self.login(account_secret=self.account_secret ,
                                                                   account_id=self.account_id
                                                                   )).grid(row=15,column=6,pady=50,ipadx=20)
        tkinter.Button(self,text="Create Stellar Account ",command=lambda:self.controller.show_pages('CreateAccount')).grid(row=15,column=4,pady=50,ipadx=20)


    def cancel(self):
         self.controller.show_pages('Login')
    def reset(self):
       
         self.account_secret.set(False)

    def save_credentials(self,account_id:str,account_secret:str):
         with open('account.csv','w') as f:
               
               f.write("account_id",account_id)
               f.write("account_secret",account_secret)
               f.close()


       
    def login(self, account_id:str=None,account_secret:str=None):
          

     
                self.account_secret = account_secret
                self.account_id = account_id

               #  if self.remember_me.get()== True:
               #       self.save_credentials(account_id=account_id,
               #                             account_secret=account_secret)
               
                self.controller.show_pages("Home")
          
    
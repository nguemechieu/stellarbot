import tkinter
from tkinter import StringVar


class Login(tkinter.Frame):

    def __init__(self, parent=None,controller=None):
        tkinter.Frame.__init__(self, parent)

        self.controller=controller
   
        self.image = tkinter.PhotoImage(file="./src/images/stellarbot.png")
        
        self.welcome_label = tkinter.Label(self, text="Welcome to StellarBot", font=("Helvetica",35),bg='green',fg='white')
        self.welcome_label.place(x=0,y=0)
     
       
        self.account_id=StringVar()
        self.account_id.set("")
      
        self.account_secret=StringVar()



        self.account_id_label = tkinter.Label(self, text="Account ID", width=20,font=("Helvetica",15), bg='green',fg='white')
        self.account_id_label.place(x=230,y=300)
        self.account_id_entry = tkinter.Entry(self, textvariable=self.account_id.get(), width=60,font=("Helvetica",15))
        self.account_id_entry.place(x=450,y=300)
        self.account_secret_label = tkinter.Label(self, text="Account Secret", width=20,font=("Helvetica",15), bg='green',fg='white')
        self.account_secret_label.place(x=230,y=400)
        self.account_secret_entry = tkinter.Entry(self, textvariable=self.account_secret.get(), width=60,font=("Helvetica",15))
        self.account_secret_entry.place(x=450,y=400)
        self.account_secret_entry.config(show="*")
        #self.account_secret_entry.focus()
        #self.account_secret_entry.bind("<Return>", self.login)


        self.create_account_button = tkinter.Button(self, text="Create Account",command=lambda: self.controller.show_pages("CreateAccount"),font=("Helvetica",15), bg='green',fg='white')   
        self.create_account_button.place(x=500,y=500)
        #self.create_account_button.bind("<Return>", self.login)

        self.login_button = tkinter.Button(self, text="Login",command=lambda: self.login(  self.account_id_entry.get(),self.account_secret.get()),font=("Helvetica",15), bg='green',fg='white')
        self.login_button.place(x=650,y=500)
      
   

        self.pack(fill=tkinter.BOTH,expand=1,side=tkinter.TOP)

        self.bind("<Return>", self.login)


        self.welcome_label.config(image=self.image,padx=0,pady=0,bg='green',fg='white',width=1530,height=800,anchor= 'n')
        self.config(bg='blue')

       
    def login(self, account_id:str=None,account_secret:str=None):
                 
                account_id =  self.controller.config['account_id']
                account_secret= self.controller.config['account_secret']
                print(account_id,account_secret)

                self.controller.account_id.set(account_id)
                self.controller.account_secret.set(account_secret)
                self.controller.show_pages("Home")
          
    
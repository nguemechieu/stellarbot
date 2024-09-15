
import tkinter as tk
import tkinter

import qrcode
from PIL import Image, ImageTk


from stellar_sdk import Keypair

class CreateAccount(tk.Frame):

    def __init__(self, parent=None,controller=None):
        super().__init__(parent)
        self.controller=controller

        self.image = tkinter.PhotoImage(file="./src/images/stellarbot.png")
        self.welcome_label = tkinter.Label(self, text="Create Stellar Lumen's Account", font=("Helvetica" ,35),bg='green',fg='white')
        self.welcome_label.place(x=0,y=0)
   
        self.account_id=tkinter.StringVar()
        self.secret_key=tkinter.StringVar()

        

        # Create  screen to display information
        self.screen_info_canvas = tkinter.Canvas(self, width=1530, height=600, background='black')
        self.screen_info_canvas.place(x=0,y=0)
        self.screen_info_canvas.create_text(300,100,text="Welcome to StellarBot  ",font=("Helvetica",15),fill='white')
        self.screen_info_canvas.create_text(400,200,text="Please click buttons to create your new account! ",font=("Helvetica",15),fill='white')
        
        self.go_back_account_button = tkinter.Button(self, text="Go Back",font=("Helvetica",15), bg='blue',fg='white',command=lambda: self.controller.show_pages("Login"))   
        self.go_back_account_button.place(x=420,y=610)


        self.create_account_button = tkinter.Button(self, text="Create New Account",command=lambda:self.create_account_now(),font=("Helvetica",15), bg='orange')
        self.create_account_button.place(x=520,y=610)

      
        self.config(bg='#1e2a38', width=1530,height = 780)
        self.welcome_label.config(image=self.image,padx=0,pady=0,bg='green',fg='white',width=1530,height=800,anchor= 'n')

        self.grid(row=0,column=0,sticky= 'nsew')
    
    def create_accounts(self):
        try:
            new_keypair = Keypair.random()
            destination_public_key = new_keypair.public_key
            return {'account_id' : destination_public_key,
                    'secret_key' : new_keypair.secret}
        except Exception as e:
           
            return  {'account_id' : '', 'secret_key' : ''}
    def create_account_now(self)->None:
     
      self.screen_info_canvas.delete('all')
      data  =self.create_accounts()
      print('data: ', data)

     
      self.account_id.set(data['account_id'])  # setting the account id to the variable for future use  (if needed)  - to be used in the login page  or any other page where you need to use the account id  - for example in the transaction page  or any other page where you need to use the account id  - for example in the transaction page  or any other page where you need to use the account id  - for

             # Create and display the QR code for the account ID
      self.generate_qr_code(account_id=self.account_id.get())

      self.screen_info_canvas.create_text(200,100, text="Account ID: ",font=("Helvetica",15),fill='white')
     
      self.secret_key_var=tkinter.StringVar()
      self.secret_key_var.set(data['secret_key'])  # setting the secret key to the variable for future use  (if needed)  - to be used in the login page  or any other page where you need to use the secret key  - for example in the transaction page  or any other page where you need to use the secret key  - for example in the transaction page  or any other page where you need to use the secret key  - for
      self.account_id_entry=tkinter.Entry(self,textvariable=self.account_id,font=("Helvetica",15),fg='green',width=250)
      self.account_id_entry.place(x=300,y=100)
      self.screen_info_canvas.create_text(200,300, text="Secret Key: ",font=("Helvetica",15),fill='white'  )
      self.secret_key_entry=tkinter.Entry(self,textvariable=self.secret_key_var,font=("Helvetica",15),fg='green',width=250)
      self.secret_key_entry.place(x=300,y=300)
      
      self.screen_info_canvas.create_text(400,550, text='Please copy and save your account id and private key.\nThen activate your account by sending some XLM into your new account!\nYou can purchase it via monpay or any crypto exchanges.\n You can also send money on this qr code',font=("Helvetica",15),fill='white')
      



    def generate_qr_code(self, account_id: str):
        # Generate a QR code for the account ID
        qr = qrcode.QRCode(
            version=1,  # Controls the size of the QR Code
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(account_id)
        qr.make(fit=True)

        # Convert the QR code into an image
        qr_img = qr.make_image(fill='black', back_color='white')

        # Save the QR code as an image
        qr_img.save("account_qr.png")

        # Display the QR code in the tkinter window
        img = Image.open("account_qr.png")
        img = img.resize((150, 150))
        self.qr_code_image = ImageTk.PhotoImage(img)

        # Add the QR code to the canvas
        self.screen_info_canvas.create_image(400, 150, image=self.qr_code_image, anchor=tkinter.NW)
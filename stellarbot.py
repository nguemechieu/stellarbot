import os
import smtplib
import tkinter
from datetime import datetime
from email.mime.text import MIMEText
from tkinter import StringVar, BOTTOM
from Login import Login
from createAccount import CreateAccount
from home import Home
from tradingbot import TradingBot
import platform
import subprocess


from marketwatch import MarketWatch
from orders import Orders


def send_email(subject: str = "", body: str = "", sender: str = "",
               recipients=None, password: str = ""):
    if recipients is None:
        recipients = ["r@gmail.com", "recipient2@gmail.com"]
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        print("Message sent!")


if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')
class StellarBot(tkinter.Tk):
    

    def __init__(self):
        tkinter.Tk.__init__(self)

        self.controller = self
        self.parent = self.master
        self.frames = {

        }

        self.account_id=StringVar()
        self.account_id.set("")
        self.account_secret=StringVar()
        self.account_secret.set("")
        
    
        self.config={ 'account_id':'GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY',
                                                                                     
                      'account_secret':'SDYAPMSEK2N4LYRFROWHE4SK4LFXF2T2OMCU3BVDAJTEAYKHT4ESKOJ6'}
        

        self.account_id.set(self.config['account_id'])
        self.account_secret.set(self.config['account_secret'])
      
        
        self.bot = TradingBot(account_id=self.controller.account_id.get(),  account_secret=  self.controller.account_secret.get())

        self.pages = {}
  
    
        self.iconbitmap("./src/images/stellarbot.ico")


        self.frames =(Login, Home, CreateAccount)
       
      
       
        
        self.show_pages("Login")
        self.mainloop()
     

    def show_pages(self, param):
        self.title("StellarBot    | AI POWERED STELLAR LUMEN NETWORK TRADER |-->    " + str(datetime.now()))
        self.geometry("1530x800")
        self.resizable(width=True, height=True)
        self.delete_frame()

        if param in ['Login', 'CreateAccount','Home']:
             frames = [ Login, Home, CreateAccount]

        for frame in frames:
                if param == frame.__name__:
                    frame = frame(self, self.controller)

                    
                    frame.tkraise()

    def delete_frame(self):
        for _frame in self.winfo_children():
            _frame.destroy()


    def show_error(self, param):
        if param is not None:
            self.Messagebox = tkinter.Message(self.master, text=param, width=300)
            print(param)
            self.Messagebox.pack(side=BOTTOM)
            self.Messagebox.after(3000, self.Messagebox.destroy)


    def exit(self):
        os._exit(1)

    def updateMe(self):
        self.update()
        self.after(1000, self.updateMe)



# If you are working in a remote Linux environment without a graphical display, you can use Xvfb (X Virtual Framebuffer) to create a virtual display and then run your tkinter code. Here's a Python script that demonstrates how to do this:



def check_os():
    system = platform.system()
    
    if system == "Windows":
        return "Windows"
    elif system == "Linux":
        return "Linux"
    elif system == "Darwin":
        return "macOS"
    else:
        return "Unknown"

if __name__ == "__main__":
     
    if check_os !="Windows":
    # Start Xvfb to create a virtual display (change the display number if needed)
     display_number = 99
     xvfb_command = f"Xvfb :{display_number} -screen 0 1280x1024x24 &"
     subprocess.Popen(xvfb_command, shell=True)

# Set the DISPLAY environment variable to point to the virtual display
     os.environ["DISPLAY"] = f":{display_number}"
  
    

    else:
     os.environ["DISPLAY"] = ":0"
    print(os.environ["DISPLAY"])
# Remember to clean up the Xvfb process when done
    subprocess.Popen(f"kill -9 $(pgrep Xvfb)", shell=True)

    print('StellarBot is running on ', check_os())
    StellarBot()

else:
    os._exit(1)
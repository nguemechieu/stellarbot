import os
import tkinter
from datetime import datetime
from tkinter import StringVar
from Login import Login
from createAccount import CreateAccount
from home import Home
from tradingbot import StellarClient
import platform
import subprocess


if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')
class StellarBot(tkinter.Tk):
    

    def __init__(self):
        tkinter.Tk.__init__(self)
        self.controller = self #reference to the controller
        self.parent = self.master #reference to the parent window
        self.frames = {

        }
        self.remember_me= tkinter.IntVar()
        self.account_id=StringVar()
        self.account_id.set("")
        self.account_secret=StringVar()
        self.account_secret.set("")
        self.time_o =tkinter.StringVar()
        self.config={ 'account_id':'GC5HLWK3OPPOFXZB674ERHOW76CFXBLBJ3DQ4RSRYUS4YVKB7SQME456',
                                                                                     
                      'account_secret':'SBXATKQLVCHN4V5FKP5LSHG222ZV7ZRO47X4FBQUPWQ2AJ6EIMWKV2AN'}#'SDYAPMSEK2N4LYRFROWHE4SK4LFXF2T2OMCU3BVDAJTEAYKHT4ESKOJ6'}
        

        self.account_id.set(self.config['account_id'].__str__())
        self.account_secret.set(self.config['account_secret'].__str__())
      
        # Initialize the TradingBot class
        self.bot = StellarClient(account_id=self.account_id.get(), secret_key=  self.account_secret.get())
        self.pages = {}
        self.iconbitmap("./src/images/stellarbot.ico")
        self.frames =(Login, Home, CreateAccount) 
        self.show_pages("Login")
        self.mainloop()
     

    def show_pages(self, param):
        self.title(  self.time_o)
        self.geometry("1530x800")
        self.resizable(width=True, height=True)
        self.delete_frame()

        if param in ['Login', 'CreateAccount','Home']:
             frames = [ Login, Home, CreateAccount]
        for frame in frames:
                if param == frame.__name__:
                    frame = frame(self, self.controller)
                    self.title(  self.time_o.get() + " | " + param)
                    frame.tkraise()

    def delete_frame(self):
        for _frame in self.winfo_children():
            _frame.destroy()



    def exit(self): # This function is called when the exit button is pressed. It
        os._exit(1)

    def updateMe(self): # This function is called every 1000 milliseconds. It updates the screen.
        self.update()
       
        self.time_o.set(datetime.now().strftime("%H:%M:%S %d/%m/%Y") +" |  WELCOME TO STELLARBOT")
        
        self.after(1000, self.updateMe)



# If you are working in a remote Linux environment without a graphical display, you can use Xvfb (X Virtual Framebuffer) to create a virtual display and then run your tkinter code. Here's a Python script that demonstrates how to do this:



def check_os():
    system = platform.system() # Get the operating system name
    
    if system == "Windows":
        return "Windows"
    if system == "Linux":
        return "Linux"
    if system == "Darwin":
        return "macOS"
    
    return "Unknown"

if __name__ == "__main__":
    if( check_os  !="Windows"):
    # Start Xvfb to create a virtual display (change the display number if needed) and then run
     display_number = 99
     xvfb_command = f"Xvfb :{display_number} -screen 0 1280x1024x24 &"
     subprocess.Popen(xvfb_command, shell=True)

# Set the DISPLAY environment variable to point to the virtual display number you just created.
     os.environ["DISPLAY"] = f":{display_number}"
    else:
     os.environ["DISPLAY"] = ":0"# Set the DISPLAY environment variable to point to the virtual display number you just created.
    print(os.environ["DISPLAY"])
    #  Clean up the Xvfb process when done
    subprocess.Popen(f"kill -9 $(pgrep Xvfb)", shell=True)

    print('StellarBot is running on ', check_os())
    StellarBot() # Run the StellarBot class
else:
    os._exit(1)
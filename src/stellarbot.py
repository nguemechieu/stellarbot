import os
import tkinter
import platform
import subprocess
from modules.frames.home import Home
from modules.frames.login import Login

from modules.frames.about import About
from modules.classes.db_manager import DatabaseManager



if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')
class StellarBot(tkinter.Tk):
    

    def __init__(self):
        tkinter.Tk.__init__(self)
        self.controller = self #reference to the controller
        self.parent = self.master #reference to the parent window
        self.frames = {}
        
        # Initialize the TradingBot class
        self.bot = None
        self.pages = {}
        self.db=DatabaseManager('stellarBot.db').db

        self.db.execute('''CREATE TABLE IF NOT EXISTS users ( 
                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                            account_id VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE, 
                            account_secret VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE,  
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.db.commit()
       
        
        self.iconbitmap("src/assets/stellarbot.ico")
        
        self.updateMe()
        self.show_pages("Login")
        self.mainloop()
     

    def show_pages(self, param):
       
        self.geometry("1530x780")
        self.resizable(width=True, height=True)
        self.delete_frame()

        if param in ['Login','Home', 'About']:
             self.frames = [Login, Home,  About]
        for frame in self.frames:
            if param == frame.__name__:
                frame = frame(self, self.controller)
                self.title(f"StellarBot@{param}")
                
    def delete_frame(self):
        for _frame in self.winfo_children():
            _frame.destroy()


    
    def exit(self): # This function is called when the exit button is pressed. It
        os._exit(1)

    def updateMe(self): # This function is called every 1000 milliseconds. It updates the screen.
        
        
        self.update()
        self.update_idletasks()
        self.after(1000, self.updateMe)
    

    def show_error_message(self, msg): # This function is called
        # Display the error message in a label

        destroy_message= tkinter.Message(self.master,text=msg)
        destroy_message.config(bg='red', fg='white')
        destroy_message.pack(fill=tkinter.BOTH, expand=True)
        




# If you are working in a remote Linux environment without a graphical display, you can use Xvfb (X Virtual Framebuffer) to create a virtual display and then run your tkinter code. Here's a Python script that demonstrates how to do this:



def check_os():
    system = platform.system() # Get the operating system name
    
    if system == "Windows":
        return "Windows"
    elif system == "Linux":
        return "Linux"
    elif system == "Darwin":
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
    subprocess.Popen("kill -9 $(pgrep Xvfb)", shell=True)

    print('StellarBot is running on ', check_os())
    StellarBot() # Run the StellarBot class
else:
    os._exit(1)
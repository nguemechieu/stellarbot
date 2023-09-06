
import tkinter
from home import Home
from tradingbot import TradingBot
from wallet import Wallet
from db import Db



class StellarBot(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.frame_list = [Home, Wallet, TradingBot]
        self.title("StellarBot")
        self.geometry("1560x800")
        self.resizable(True, True)
       
        self.iconbitmap('images/stellarbot.ico')
        #self.db = Db()
        self.iconphoto(True, tkinter.PhotoImage(file="images/stellarbot.png"))
        welcome= tkinter.Label(self.master, text="Welcome to StellarBot", bg="white", fg="green", font=("Arial", 40))
        welcome.grid(row=2,column=1,)
                             
        
        
        tkinter.Label(self.master, text="Account ID", font=("Arial", 10)).grid(row=15,column=2)

    




        acc = tkinter.StringVar()
        acc.set("Enter Account ID")
        tkinter.Entry(self.master, textvariable=acc).grid(row=15
                                                   , column=3
                                                   )
        tkinter.Label(self.master, text="Secret Key", font=("Arial", 10)).grid(row=16, column=2)
        sec = tkinter.StringVar()
        sec.set("Enter Secret Key")
        tkinter.Entry(self.master, textvariable=sec).grid(row=16, column=3)
        tkinter.Button(self.master, text="Login", command=lambda:self.login(user_id=acc,secret_key=sec)).grid(row=11, column=10)
        self.bot = TradingBot(controller=self)
       
        self.config(bg='lightblue',border=8,relief='ridge', width=1560, height=800)
      
        self.mainloop()

    def login(self, user_id, secret_key):
  
        # self.db.create_table()
        # try:
        #     self.bot.login(user_id, secret_key)
        # except Exception as e:
        #     tkinter.Message(text=str(e))
        # pass
        self.show_frame("Home")
        

    def show_frame(self, frame :tkinter.Frame=None):

         for fram in self.winfo_children():
            fram.destroy()
        
        
         self.config(self.master,bg='lightblue',border=11,relief='ridge')

         for fram in self.frame_list:
             if fram.__name__ == frame:
                 fram.tkraise()



         
        

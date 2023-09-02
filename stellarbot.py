import tkinter

from tradingbot import TradingBot


class StellarBot(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.title("StellarBot")
        self.geometry("1560x800")
        self.resizable(True, True)
        self.configure(bg="black")
        self.iconbitmap("sellarbot.ico")

        self.bot = TradingBot()

        self.mainloop()

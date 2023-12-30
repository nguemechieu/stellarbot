from tkinter import Frame, Label, ttk
class MarketWatch(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.list_view = None
        self.on_double_click = None
        self.label = None
        self.controller = controller
        self.parent = parent
        self.init_ui()
    def init_ui(self):
        self.parent.title("Market Watch")
        self.label = Label(self, text="Market Watch")
        self.label.pack()
        self.list_view = ttk.Treeview(self, columns=(" Symbol", "Price", "Change", "Volume", "Open", "High", "Low",
                                                     "Close",
                                                     "Adj Close", "Market Cap", "P/E Ratio"))
        self.list_view.pack()
        self.list_view.info()
        self.list_view.bind("<Double-Button-1>", self.on_double_click)
        self.pack()
        self.list_view.heading("Symbol", text="Symbol")
        self.list_view.heading("Price", text="Price")
        self.list_view.heading("Change", text="Change")
        self.list_view.heading("Volume", text="Volume")
        


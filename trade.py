from tkinter import Frame, BOTH
class Trade(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.init_ui()

    def trade_history(self):
        self.controller.trade_history()

    def trade_buy(self, price, quantity, order_type):
        self.controller.trade_buy(price, quantity, order_type)

    def trade_sell(self, price, quantity, order_type):
        self.controller.trade_sell(price, quantity, order_type)

    def init_ui(self):
        self.pack(fill=BOTH, expand=1)
        pass

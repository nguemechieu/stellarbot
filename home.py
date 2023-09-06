from datetime import datetime
from tkinter import LEFT, TOP, Frame, BOTH, Label


class Home(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
     
        self.controller = controller
        self.parent = parent
        self.Label1 = Label(self.parent, text="Stellar DEX")
        self.Label1.grid(row=1, column=1)
        time_current = datetime.datetime.utcnow()

        self.time_label = Label(self.parent, text=time_current,bg='green')
        self.time_label.grid(row=4, column=3)
        self.init_ui()
        self.parent.pack()
    

    def init_ui(self):
       

        self.trade_info = { "Exchange": "Stellar DEX",
    "Assets": "Lumens",
    "Trading Pair": "USD Coin (centre.io)",
    "Current Price": "0.1243191 USDC (+1.44%)",
    "High": "0.1428571",
    "Low": "0.1211291",
    "Market Stats": {
        "XLM Price": "0.1228791 USDC",
        "24h Change": "1.44%",
        "24h Volume": "930592 USDC ($929478.695)",
        "Bid-Ask Spread": "0.2841%",
    },
    "New Order": {
        "Buy": {
            "Type": "Limit",
            "Amount": "XLM",
            "Price": "0.124621 USDC",
            "Total": "USDC",
        },
        "Sell": {
            "Type": "Limit",
            "Amount": "USDC",
            "Price": "0.124621 USDC",
            "Total": "XLM",
        },},
        "Order Book": [
        {"Price (USDC)": "0.1252", "Amount (XLM)": "39.9930408", "Total (USDC)": "5.0071287"},
        {"Price (USDC)": "0.1252", "Amount (XLM)": "7.1001945", "Total (USDC)": "0.8889443"},
        {"Price (USDC)": "0.125133", "Amount (XLM)": "1135.3872496", "Total (USDC)": "142.0744127"},
        {"Price (USDC)": "0.1251233", "Amount (XLM)": "27312.14", "Total (USDC)": "3417.3850868"},],}
        

         # Print the trade frame
        print("Trade")
        print(f"Exchange: {self.trade_info['Exchange']}")
        print(f"Assets: {self.trade_info['Assets']}")
        print(f"Trading Pair: {self.trade_info['Trading Pair']}")
        print(f"Current Price: {self.trade_info['Current Price']}")
        print(f"High: {self.trade_info['High']}")
        print(f"Low: {self.trade_info['Low']}")
        print("\nMarket Stats:")
        for key, value in self.trade_info['Market Stats'].items():
         print(f"{key}: {value}")
        print("\nNew Order:")
        for order_type, order_details in self.trade_info['New Order'].items():

          print(f"{order_type}:")
        for key, value in order_details.items():
         print(f"{key}: {value}")
        print("\nOrder Book:")
        for order in self.trade_info['Order Book']:
         print(f"Price (USDC): {order['Price (USDC)']}, Amount (XLM): {order['Amount (XLM)']}, Total (USDC): {order['Total (USDC)']}")


        self.Label1.bind("<Button-1>", lambda e: self.controller.show_frame(frame="Login"))
        

  
          

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to fetch market data from Stellar Horizon API
def fetch_market_data():
    url = 'https://horizon.stellar.org/order_book/USDC:GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN/native'
    response = requests.get(url)
    return response.json()

# Function to update the order book display
def update_order_book():
    market_data = fetch_market_data()

    # Clear existing rows in the order book tables
    for i in order_book_bids.get_children():
        order_book_bids.delete(i)
    for i in order_book_asks.get_children():
        order_book_asks.delete(i)

    # Insert bids into the order book
    for bid in market_data['bids']:
        order_book_bids.insert("", "end", values=(bid['price'], bid['amount']))

    # Insert asks into the order book
    for ask in market_data['asks']:
        order_book_asks.insert("", "end", values=(ask['price'], ask['amount']))

    # Update the price chart
    update_price_chart(market_data)

# Function to update the price chart
def update_price_chart(market_data):
    bids = [float(bid['price']) for bid in market_data['bids']]
    asks = [float(ask['price']) for ask in market_data['asks']]

    # Clear the current plot
    fig.clear()
    ax = fig.add_subplot(111)

    # Plot bids and asks
    ax.plot(bids, label='Bids', marker='o', linestyle='-', color='green')
    ax.plot(asks, label='Asks', marker='o', linestyle='-', color='red')

    # Chart settings
    ax.set_title('Bid/Ask Prices')
    ax.set_xlabel('Order Index')
    ax.set_ylabel('Price')
    ax.legend()

    # Draw the updated canvas
    canvas.draw()

# Main window setup
root = tk.Tk()
root.title("Stellar USDC Market Dashboard")
root.geometry("1000x700")

# Create a style for the Treeview (for tables)
style = ttk.Style()
style.configure("Treeview", rowheight=25)

# Heading Label
heading_label = ttk.Label(root, text="Stellar USDC Market Dashboard", font=("Helvetica", 16))
heading_label.pack(pady=10)

# Frame for Order Book
order_book_frame = ttk.Frame(root)
order_book_frame.pack(pady=10)

# Label for Order Book
order_book_label = ttk.Label(order_book_frame, text="Order Book", font=("Helvetica", 12))
order_book_label.grid(row=0, column=0, columnspan=2, pady=5)

# Order Book - Bids Table
order_book_bids_label = ttk.Label(order_book_frame, text="Bids", font=("Helvetica", 10))
order_book_bids_label.grid(row=1, column=0, pady=5)

order_book_bids = ttk.Treeview(order_book_frame, columns=("Price", "Amount"), show="headings", height=8)
order_book_bids.heading("Price", text="Price")
order_book_bids.heading("Amount", text="Amount")
order_book_bids.grid(row=2, column=0)

# Order Book - Asks Table
order_book_asks_label = ttk.Label(order_book_frame, text="Asks", font=("Helvetica", 10))
order_book_asks_label.grid(row=1, column=1, pady=5)

order_book_asks = ttk.Treeview(order_book_frame, columns=("Price", "Amount"), show="headings", height=8)
order_book_asks.heading("Price", text="Price")
order_book_asks.heading("Amount", text="Amount")
order_book_asks.grid(row=2, column=1)

# Frame for the chart
chart_frame = ttk.Frame(root)
chart_frame.pack(pady=20)

# Create Matplotlib Figure and add to the Tkinter window
fig = Figure(figsize=(6, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.get_tk_widget().pack()

# Update button to refresh data
update_button = ttk.Button(root, text="Update Dashboard", command=update_order_book)
update_button.pack(pady=20)
if __name__ == "__main__":
# Run the main loop
 root.mainloop()

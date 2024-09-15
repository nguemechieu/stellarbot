import tkinter as tk

class About(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        # Set the background color
        self.configure(bg='#1e2a38')
        
        # Title label
        title = tk.Label(self, text="About StellarBot", font=("Helvetica", 24), fg="white", bg="#1e2a38")
        title.pack(pady=20)
        self.place(x=0, y=0, width=1530, height=780)
        # About description
        about_text = """
        StellarBot is an open-source project aimed at providing a 
        comprehensive platform for automated trading on the Stellar network.
        
        This bot leverages machine learning techniques to predict market trends 
        and execute trades based on live data. StellarBot supports various trading 
        pairs and allows users to create or close orders according to their 
        preferences.

        Author: nguemechieu
        GitHub: https://github.com/nguemechieu/stellarbot
        
        """
        about_label = tk.Label(self, text=about_text, font=("Helvetica", 14), fg="white", bg="#1e2a38", justify="left")
        about_label.pack(pady=20)
        
        # Back button to navigate to other frames
        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("Home"), bg="white", fg="#1e2a38")
        back_button.pack(pady=10)

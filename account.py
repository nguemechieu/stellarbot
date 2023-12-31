
import tkinter
from tkinter import ttk

import pandas as pd


class Account(ttk.Frame):

    def __init__(self):

        ttk.Frame.__init__(self)
        

        tkinter.Label(self,text='Account').grid(row=1,column=0)

        self.listbox=tkinter.Listbox(self)
        self.listbox.grid(row=3,column=1
                          )
        read=pd.read_csv('account.csv')
        self.listbox.insert( 'balance', read)
     

    
    
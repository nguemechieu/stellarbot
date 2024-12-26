import tkinter as tk
from tkinter import ttk
import pandas as pd
import requests
from PyQt5.QtWidgets import QWidget
from stellar_sdk import Asset


# Define the schema structure
class MarketSchema:
    def __init__(self):
        self.bids = []
        self.asks = []
        self.base = {
            'asset_code': 'USD',
            'asset_issuer': 'GAAQ56B55K6276J2T67C5Z7Z356422J57443Z7A2',
            'asset_type': 'credit_alphanum4'
        }
        self.counter = {
            'asset_code': 'USDC',
            'asset_issuer': 'GAAQ56B55K6276J2T67C5Z7Z356422J57443Z7A2',
            'asset_type': 'credit_alphanum4'
        }

    def populate_bids(self, bids_data):
        """Populate bids list with data"""
        for bid in bids_data:
            self.bids.append({
                'price': bid['price'],
                'amount': bid['amount']
            })

    def populate_asks(self, asks_data):
        """Populate asks list with data"""
        for ask in asks_data:
            self.asks.append({
                'price': ask['price'],
                'amount': ask['amount']
            })

    def get_schema(self):
        """Return the complete schema"""
        return {
            'bids': self.bids,
            'asks': self.asks,
            'base': self.base,
            'counter': self.counter
        }


def fetch_market_data(base_asset, counter_asset):
    market_schema = MarketSchema()

    url = "https://horizon.stellar.org/order_book"
    params = {
        'base_asset_type': base_asset['asset_type'],
        'base_asset_code': base_asset['asset_code'],
        'base_asset_issuer': base_asset['asset_issuer'],
        'counter_asset_type': counter_asset['asset_type'],
        'counter_asset_code': counter_asset['asset_code'],
        'counter_asset_issuer': counter_asset['asset_issuer']
    }

    # Filter out None values from params
    params = {k: v for k, v in params.items() if v is not None}

    try:
        return _extracted_from_fetch_market_data_18(url, params, market_schema)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market data: {e}")
        return None

def _extracted_from_fetch_market_data_18(url, params, market_schema):
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Get bids and asks from the API response
    data = response.json()
    bids_data = data.get('bids', [])
    asks_data = data.get('asks', [])

    # Populate the schema
    market_schema.populate_bids(bids_data)
    market_schema.populate_asks(asks_data)
    return market_schema.get_schema()


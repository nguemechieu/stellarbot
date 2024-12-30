import logging
import os
import pandas as pd
import requests


class BlockchainAsset:
    CSV_FILE_PATH = 'stellar_bot_blockchain_assets.csv'

    def __init__(self, code: str, issuer: str, amount: float, image: str, homepage: str, current_price: float = None):
        """
        Initialize the BlockchainAsset object.
        """
        self.logger = logging.getLogger(__name__)
        self.code = code
        self.issuer = issuer
        self.amount = amount
        self.image = image
        self.current_price = current_price or 0.0  # Set the current price to 0.0 if not provided in usd dollars.
        self.homepage = homepage
        self.logger.info("BlockchainAsset initialized successfully.")
        self.asset_info_df = pd.DataFrame({
            'code': [self.code],
            'issuer': [self.issuer],
            'amount': [self.amount],
            'image': [self.image],
            'homepage': [self.homepage]
        })
        self.save_asset_info()

    def save_asset_info(self):
        """
        Save the asset information to a CSV file.
        """
        try:
            if os.path.exists(self.CSV_FILE_PATH):
                existing_data = pd.read_csv(self.CSV_FILE_PATH)
                self.asset_info_df = pd.concat([existing_data, self.asset_info_df], ignore_index=True).drop_duplicates(subset=['code'], keep='last')
            self.asset_info_df.to_csv(self.CSV_FILE_PATH, index=False)
            self.logger.info(f"Asset information saved successfully to {self.CSV_FILE_PATH}.")
        except Exception as e:
            self.logger.error(f"Error saving asset information: {e}")

    def get_asset_info_df(self):
        """
        Retrieve asset information from the CSV file as a DataFrame.
        """
        try:
            if not os.path.exists(self.CSV_FILE_PATH):
                self.logger.warning(f"No asset information found in {self.CSV_FILE_PATH}.")
                return pd.DataFrame()
            self.asset_info_df = pd.read_csv(self.CSV_FILE_PATH)
            self.logger.info("Asset information retrieved successfully.")
            return self.asset_info_df
        except Exception as e:
            self.logger.error(f"Error retrieving asset information: {e}")
            return pd.DataFrame()

    def update_asset_info_csv(self, new_code: str, new_issuer: str, new_amount: float, new_image: str, new_homepage: str):
        """
        Update the asset information in the CSV file.
        """
        try:
            self.asset_info_df.loc[0, 'code'] = new_code
            self.asset_info_df.loc[0, 'issuer'] = new_issuer
            self.asset_info_df.loc[0, 'amount'] = new_amount
            self.asset_info_df.loc[0, 'image'] = new_image
            self.asset_info_df.loc[0, 'homepage'] = new_homepage
            self.asset_info_df.to_csv(self.CSV_FILE_PATH, index=False)
            self.logger.info(f"Asset information updated successfully in {self.CSV_FILE_PATH}.")
        except Exception as e:
            self.logger.error(f"Error updating asset information: {e}")

    def find_asset(self, code: str):
        """
        Find and return asset information by code.
        """
        try:
            if not os.path.exists(self.CSV_FILE_PATH):
                self.logger.warning("No asset information available to search.")
                return None
            data = pd.read_csv(self.CSV_FILE_PATH)
            asset = data[data['code'] == code]
            if not asset.empty:
                self.logger.info(f"Asset found: {code}")
                return asset
            else:
                self.logger.warning(f"Asset not found: {code}")

                return None
        except Exception as e:
            self.logger.error(f"Error finding asset: {e}")
            return None

    def validate_asset_info(self):
        """
        Validate the asset's information.
        """
        if not isinstance(self.code, str) or not isinstance(self.issuer, str) or not isinstance(self.amount, (int, float)) or not isinstance(self.image, str) or not isinstance(self.homepage, str):
            raise ValueError("Invalid asset information provided.")
        if len(self.code) > 10 or len(self.issuer) > 255 or len(self.image) > 255 or len(self.homepage) > 255:
            raise ValueError("Asset information exceeds maximum length.")
        if self.amount <= 0:
            raise ValueError("Invalid asset amount provided.")
        if not self.image.startswith("http"):
            raise ValueError("Invalid image URL provided.")
        if not self.homepage.startswith("http"):
            raise ValueError("Invalid homepage URL provided.")
        self.logger.info("Asset information is valid.")

    def transfer_asset(self, recipient_account_id: str, amount: float):
        """
        Simulate the transfer of assets.
        """
        if not isinstance(recipient_account_id, str) or not isinstance(amount, (int, float)):
            raise ValueError("Invalid recipient account ID or amount provided.")
        if amount <= 0:
            raise ValueError("Invalid transfer amount provided.")
        if self.amount < amount:
            raise ValueError("Insufficient balance to transfer.")
        self.amount -= amount
        self.logger.info(f"Transferred {amount} {self.code} to {recipient_account_id}.")
        return f"Transferred {amount} {self.code} to {recipient_account_id}."

    def __str__(self):
        """
        String representation of the BlockchainAsset object.
        """
        return f"{self.code} - {self.issuer} - {self.amount} - {self.image} - {self.homepage}"




    # Convert price to any desired currency using an API or a local currency conversion tool.
    def convert_price_to_currency(self, currency: str):
        """
        Convert the asset's current price to a different currency using an API or a local currency conversion tool.

        Parameters:
        currency (str): The desired currency (e.g., USD, EUR, GBP).

        Returns:
        float: The converted price in the desired currency.
        """
        # Implement a currency conversion API call or use a local currency conversion tool to convert the price.
        # Example implementation using a currency conversion API:
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}")
        if response.status_code == 200:
            conversion_rate = response.json()["rates"][self.code]
            return self.current_price * conversion_rate
        else:
            self.logger.error(f"Error converting price to {currency}: {response.text}")

            raise ValueError(f"Error converting price to {currency}: {response.text}")
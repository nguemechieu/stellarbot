import sqlite3
import logging

class DatabaseManager:
    """
    DatabaseManager class handles all interactions with the SQLite database for storing assets, OHLCV data,
    and other related information. It abstracts away the database operations and provides methods
    to create, insert, query, and delete data.
    """
    def __init__(self, db_path="stellarBot.db"):
        """
        Initializes the DatabaseManager instance with a SQLite connection.

        Parameters:
        - db_path (str): Path to the SQLite database file. Defaults to 'stellarBot.db'.
        """
        self.db = sqlite3.connect(db_path)
        self.logger = logging.getLogger(__name__)
        self.create_tables()

    def create_tables(self):
        """
        Creates the required tables in the database if they do not exist. 
        This includes tables for assets and OHLCV data.
        """
        try:
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    asset_code TEXT NOT NULL, 
                    asset_issuer TEXT NOT NULL
                )
            ''')
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS ohlcv_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    account_id TEXT NOT NULL, 
                    open_time TEXT NOT NULL, 
                    close_time TEXT NOT NULL, 
                    low TEXT NOT NULL, 
                    high TEXT NOT NULL, 
                    close TEXT NOT NULL, 
                    volume TEXT NOT NULL
                )
            ''')
            self.db.commit()
            self.logger.info("Tables created successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating tables: {e}")

    def insert_asset(self, asset_code, asset_issuer):
        """
        Inserts a new asset into the assets table.

        Parameters:
        - asset_code (str): The code representing the asset (e.g., XLM, BTC).
        - asset_issuer (str): The issuer of the asset.

        Returns:
        - bool: True if the insertion was successful, False otherwise.
        """
        try:
            return self._extracted_from_delete_asset_13(
                'INSERT INTO assets (asset_code, asset_issuer) VALUES (?, ?)',
                asset_code,
                asset_issuer,
                'Inserted asset: ',
            )
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting asset: {e}")
            return False

    def insert_ohlcv_data(self, account_id, open_time, close_time, low, high, close, volume):
        """
        Inserts OHLCV (Open, High, Low, Close, Volume) data into the ohlcv_data table.

        Parameters:
        - account_id (str): The account ID.
        - open_time (str): The opening time of the candle.
        - close_time (str): The closing time of the candle.
        - low (str): The lowest price during the period.
        - high (str): The highest price during the period.
        - close (str): The closing price.
        - volume (str): The trading volume during the period.

        Returns:
        - bool: True if the insertion was successful, False otherwise.
        """
        try:
            self.db.execute('''
                INSERT INTO ohlcv_data (account_id, open_time, close_time, low, high, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (account_id, open_time, close_time, low, high, close, volume))
            self.db.commit()
            self.logger.info(f"Inserted OHLCV data for account {account_id}")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting OHLCV data: {e}")
            return False

    def get_assets(self):
        """
        Fetches all assets from the assets table.

        Returns:
        - list: A list of tuples representing all the assets, or an empty list in case of an error.
        """
        try:
            cursor = self.db.execute('SELECT asset_code, asset_issuer FROM assets')
            assets = cursor.fetchall()
            self.logger.info("Fetched all assets")
            return assets
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching assets: {e}")
            return []

    def get_ohlcv_data(self, account_id):
        """
        Fetches OHLCV data for a specific account.

        Parameters:
        - account_id (str): The account ID for which to fetch the OHLCV data.

        Returns:
        - list: A list of tuples representing the OHLCV data, or an empty list in case of an error.
        """
        try:
            cursor = self.db.execute('SELECT * FROM ohlcv_data WHERE account_id = ?', (account_id,))
            ohlcv_data = cursor.fetchall()
            self.logger.info(f"Fetched OHLCV data for account {account_id}")
            return ohlcv_data
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching OHLCV data: {e}")
            return []

    def delete_asset(self, asset_code, asset_issuer):
        """
        Deletes an asset from the assets table based on asset code and issuer.

        Parameters:
        - asset_code (str): The asset code to delete (e.g., XLM, BTC).
        - asset_issuer (str): The issuer of the asset.

        Returns:
        - bool: True if the deletion was successful, False otherwise.
        """
        try:
            return self._extracted_from_delete_asset_13(
                'DELETE FROM assets WHERE asset_code = ? AND asset_issuer = ?',
                asset_code,
                asset_issuer,
                'Deleted asset: ',
            )
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting asset: {e}")
            return False

    # TODO Rename this here and in `insert_asset` and `delete_asset`
    def _extracted_from_delete_asset_13(self, arg0, asset_code, asset_issuer, arg3):
        self.db.execute(arg0, (asset_code, asset_issuer))
        self.db.commit()
        self.logger.info(f"{arg3}{asset_code} - {asset_issuer}")
        return True

    def close(self):
        """
        Closes the database connection.
        """
        try:
            self.db.close()
            self.logger.info("Database connection closed")
        except sqlite3.Error as e:
            self.logger.error(f"Error closing database: {e}")

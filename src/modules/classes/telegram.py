import logging
import os
import time
from datetime import datetime
from enum import Enum
from threading import Lock, Thread

import pyautogui
import requests


class Actions(Enum):
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    TYPING = "typing"
    JOIN_CHANNEL = "join_channel"
    UPLOAD_PHOTO = "upload photo"
    UPLOAD_VIDEO = "upload video"
    UPLOAD_AUDIO = "upload audio"
    UPLOAD_DOCUMENT = "upload document"
    LOCATION = "location"
    CONTACT = "contact"
    VIDEO_CALL = "video_call"
    FILE_UPLOAD = "file_upload"
    GIF = "gif"
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    VIDEO = "video"
    RECORDING = "recording"


def create_keyboard(buttons: list) -> list:
    """
    Create a keyboard layout for a Telegram bot.

    Args:
    buttons (list): A list of button labels.

    Returns:
    list: A list of keyboard layout rows.
    """
    return [[button] for button in buttons]


def save_screenshot(file_path):
    """
    Save the screenshot to a JPEG file.

    Args:
    file_path (str): The path where the screenshot will be saved.
    """
    screen = pyautogui.screenshot()
    screen.save(file_path)


class TelegramBot:
    """
    This class represents a Telegram bot.
    """

    def __init__(self, token: str):
        self.lock = Lock()
        self.token = token
        self.updates = []  # List to store incoming updates from the Telegram bot
        self.server_msg = {}  # Dictionary to store the server message data received from the Telegram bot
        self.update_id = 0  # ID of the last received update

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.info("TelegramBot initialized")
        self.chat_id = None  # ID of the channel to join
        # Set the server message data
        self.server_msg['status'] = "stopped"
        self.server_msg['message'] = "StellarBot is not running."

        # Set up the HTTP client for making requests to the Telegram API
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

        # Set up the HTTP client for making requests to the Stellar network
        self.stellar_session = requests.Session()
        self.stellar_session.headers.update({"Content-Type": "application/json"})
        self.stellar_session.headers.update({"X-User-Agent": "StellarBot"})

        self.thread = Thread(target=self.run(), daemon=True)
        self.thread.start()

    def get_actions(self) -> list:

        # Fetch new updates from the Telegram bot
        updates = self.process_http_request("getUpdates", {"offset": self.update_id + 1})

        # Store the updates in the internal list
        self.updates.extend(updates.get("result", []))

        # Update the update ID for the next request
        self.update_id = updates["result"][-1]["update_id"]

        # Return the list of new actions
        return [update["message"]["text"] for update in self.updates if "text" in update["message"]]

    def process_http_request(self, method: str, params: dict) -> dict:
        """
        Process HTTP requests to the Telegram API.

        Args:
        method (str): The HTTP method to be used.
        params (dict): The parameters to be included in the request.

        Returns:
        dict: A dictionary containing the response data from the Telegram API.
        """
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        response = self.session.post(url, json=params)

        if response.status_code != 200:
            self.logger.error(f"Error processing HTTP request: {response.status_code} - {response.text}")
            return {}

        return response.json()

    def send_action(self, chat_id: int, action: Actions ):
        """
        Send an action to a Telegram chat.
        Args:
        chat_id (int): The ID of the chat where the action will be sent.
        action (Actions): The action to be performed.
        data (dict, optional): Additional data to be included in the action request.

        """
        params = {
            "chat_id": chat_id,
            "action": action.value
        }


        self.process_http_request("sendChatAction", params)

    def send_reply_keyboard(self, chat_id: int, keyboard: list):
        """
        Send a reply keyboard to a Telegram chat.

        Args:
        chat_id (int): The ID of the chat where the keyboard will be sent.
        keyboard (list): The keyboard layout to be sent.
        """
        params = {
            "chat_id": chat_id,
            "reply_markup": {
                "keyboard": keyboard,
                "resize_keyboard": True,
                "one_time_keyboard": True
            }
        }
        self.process_http_request("sendMessage", params)

    def get_command(self, message: str) -> str:
        """
        # Extract the command from the message
        return message.split("/")[1] if message.startswith("/") else ""
        """
        self.logger.info(f"Received message: {message}")
        return message.split("/")[1] if message.startswith("/") else ""

    def process_message(self, message: dict):
        """
        Process incoming messages from the Telegram bot.

        Args:
        message (dict): A dictionary containing the message data.
        """
        # Extract the command from the message
        command = self.get_command(message["text"])
        # Perform actions based on the command and tracking chat state to respond to the user
        self.chat_id = message["chat"]["id"]

        if command == "start":
            state = 1

            self.server_msg['status'] = "running"
            self.server_msg['message'] = "StellarBot is running."
            self.send_reply_keyboard(message["chat"]["id"], create_keyboard([
                "Start",
                "Account",
                "Trading",
                "news",
                "Settings",
                "Screenshot",
                "Analysis",
                "Subscribe",
                "Unsubscribe",
                "Status",
                "Balance",
                "Transactions",
                "Stellar",
                "Profitability",
                "Performance",
                "Market",
                "Market Cap",
                "Price",
                "Volume",
                "24h High",
                "24h Low",
                "24h Open",
                "24h Close",
                "24h Volume",
                "Market Cap Rank",
                "Circulating Supply",
                "Total Supply",
                "IPO",
                "Dividend",
                "Exchange Rate",
                "Currency",
                "Fiat",
                "Fiat to Stellar",
                "Stellar to Fiat",
                "Report",
                "Help"
            ]))
        elif command == "help":
            state = 2
            self.send_message(message["chat"]["id"],
                              "Welcome to the StellarBot Help Center! Here you will find all the resources and information you need to get started, troubleshoot issues, and explore features.")
            self.send_message(message["chat"]["id"],
                              "StellarBot is a simple Telegram bot that interacts with the Stellar network.")
        elif command == "trading":
            state = 3
            self.send_message(message["chat"]["id"],
                              "StellarBot allows you to trade assets on the Stellar network. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Create a Stellar account: https://www.stellar.org/get-started/")


        elif command == "account":
            state = 5
            self.send_message(message["chat"]["id"],
                              "StellarBot allows you to manage your Stellar account. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Create a Stellar account: https://www.stellar.org/get-started/")
            self.send_message(message["chat"]["id"], "2. Set up a wallet: https://www.stellar.org/wallets/")
            self.send_message(message["chat"]["id"],
                              "3. Fund your account: https://www.stellar.org/learn/tutorials/stellar-basics/how-to-fund-a-new-account/")

        elif command == "news":
            state = 6
            self.send_message(message["chat"]["id"],
                              "StellarBot provides real-time news updates about the Stellar network. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Subscribe to news channels: https://www.stellar.org/news/subscribe/")
            self.send_message(message["chat"]["id"], "2. Read articles: https://www.stellar.org/blog/")

        elif command == "settings":
            state = 7
            self.send_message(message["chat"]["id"],
                              "StellarBot allows you to customize your bot's settings. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Set up a Telegram bot: https://core.telegram.org/bots#3-how-to-create-a-bot")
            self.send_message(message["chat"]["id"],
                              "2. Configure the bot: https://core.telegram.org/bots/api#setwebhook")
            self.send_message(message["chat"]["id"],
                              "3. Set up a webhook: https://core.telegram.org/bots/api#setwebhook")

        elif command == "screenshot":
            state = 8
            self.send_message(message["chat"]["id"],
                              "StellarBot allows you to take screenshots of your bot's interface. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Enable screenshots: https://core.telegram.org/bots/api#setwebhook")
            self.send_message(message["chat"]["id"],
                              "2. Configure the bot: https://core.telegram.org/bots/api#setwebhook")
            self.send_message(message["chat"]["id"],
                              "3. Set up a webhook: https://core.telegram.org/bots/api#setwebhook")

        elif command == "analysis":
            state = 9
            self.send_message(message["chat"]["id"],
                              "StellarBot provides analysis tools for your Stellar network. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Subscribe to news channels: https://www.stellar.org/news/subscribe/")
            self.send_message(message["chat"]["id"], "2. Read articles: https://www.stellar.org/blog/")
            self.send_message(message["chat"]["id"],
                              "3. Use StellarBot's analysis tools: https://www.stellar.org/blog/")

        elif command == "subscribe":
            state = 10
            self.send_message(message["chat"]["id"],
                              "StellarBot allows you to subscribe to news channels. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Subscribe to news channels: https://www.stellar.org/news/subscribe/")
            self.send_message(message["chat"]["id"], "2. Read articles: https://www.stellar.org/blog/")

        elif command == "unsubscribe":
            state = 11
            self.send_message(message["chat"]["id"],
                              "StellarBot allows you to unsubscribe from news channels. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Subscribe to news channels: https://www.stellar.org/news/subscribe/")
            self.send_message(message["chat"]["id"], "2. Read articles: https://www.stellar.org/blog/")

        elif command == "status":
            state = 12
            self.send_message(message["chat"]["id"], f"StellarBot Status: {self.server_msg['status']}")
            self.send_message(message["chat"]["id"], self.server_msg['message'])


        elif command == "balance":
            state = 13
            self.send_message(message["chat"]["id"],
                              "StellarBot doesn't have real-time balance information. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Create a Stellar account: https://www.stellar.org/get-started/")
            self.send_message(message["chat"]["id"], "2. Set up a wallet: https://www.stellar.org/wallets/")
            self.send_message(message["chat"]["id"],
                              "3. Fund your account: https://www.stellar.org/learn/tutorials/stellar-basics/how-to-fund-a-new-account/")

        elif command == "transactions":
            state = 14
            self.send_message(message["chat"]["id"],
                              "StellarBot doesn't have real-time transaction information. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Create a Stellar account: https://www.stellar.org/get-started/")
            self.send_message(message["chat"]["id"], "2. Set up a wallet: https://www.stellar.org/wallets/")
            self.send_message(message["chat"]["id"],
                              "3. Fund your account: https://www.stellar.org/learn/tutorials/stellar-basics/how-to-fund-a-new-account/")

        elif command == "stellar":
            state = 15
            self.send_message(message["chat"]["id"],
                              "StellarBot doesn't have real-time Stellar information. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Create a Stellar account: https://www.stellar.org/get-started/")
            self.send_message(message["chat"]["id"], "2. Set up a wallet: https://www.stellar.org/wallets/")
            self.send_message(message["chat"]["id"],
                              "3. Fund your account: https://www.stellar.org/learn/tutorials/stellar-basics/how-to-fund-a-new-account/")

        elif command == "trade":
            state = 16
            self.send_message(message["chat"]["id"],
                              "StellarBot doesn't have real-time trade information. To get started, please follow these steps:")
            self.send_message(message["chat"]["id"],
                              "1. Create a Stellar account: https://www.stellar.org/get-started/")
            self.send_message(message["chat"]["id"], "2. Set up a wallet: https://www.stellar.org/wallets/")
            self.send_message(message["chat"]["id"],
                              "3. Fund your account: https://www.stellar.org/learn/tutorials/stellar-basics/how-to-fund-a-new-account/")













        else:
            state = 4
            self.send_message(message["chat"]["id"],
                              "I'm sorry, but I don't understand that command. Please try again.")
            self.send_message(message["chat"]["id"], "Invalid command. Use /start to start the bot.")
        self.process_state(state)

    def send_message(self, chat_id: int, message: str):
        """
        Send a message to a Telegram chat.

        Args:
        chat_id (int): The ID of the chat where the message will be sent.
        message (str): The message to be sent.
        """

        if chat_id is None:
            chat_id = self.chat_id

        self.send_action(chat_id, Actions.TYPING)
        params = {
            "chat_id": chat_id,
            "text": message
        }
        self.process_http_request("sendMessage", params)

    def send_photo(self, chat_id: int, photo_path: str):
        """
        Send a photo to a Telegram chat.

        Args:
        chat_id (int): The ID of the chat where the photo will be sent.
        photo_path (str): The path to the photo file.
        """
        self.send_action(chat_id, Actions.UPLOAD_PHOTO)
        params = {
            "chat_id": chat_id,
            "photo": open(photo_path, "rb")
        }

        self.process_http_request("sendPhoto", params)

    def send_audio(self, chat_id: int, audio_path: str):
        """
        Send an audio file to a Telegram chat.

        Args:
        chat_id (int): The ID of the chat where the audio will be sent.
        audio_path (str): The path to the audio file.
        """
        self.send_action(chat_id, Actions.UPLOAD_AUDIO)
        params = {
            "chat_id": chat_id,
            "audio": open(audio_path, "rb")
        }
        self.process_http_request("sendAudio", params)

    def send_document(self, chat_id: int, document_path: str):
        """
        Send a document to a Telegram chat.

        Args:
        chat_id (int): The ID of the chat where the document will be sent.
        document_path (str): The path to the document file.
        """
        self.send_action(chat_id=chat_id, action=Actions.UPLOAD_DOCUMENT)
        params = {
            "chat_id": chat_id,
            "document": open(document_path, "rb")
        }
        self.process_http_request("sendDocument", params)

    def get_updates(self, offset: int = 0, limit: int = 100) -> list:
        """
        Retrieve updates from the Telegram bot.

        Args:
        offset (int, optional): The offset for pagination. Defaults to 0.
        limit (int, optional): The maximum number of updates to return. Defaults to 100.

        Returns:
        list: A list of updates.
        """
        self.send_action(self.updates[-1]['update_id'] + 1, Actions.TYPING)
        params = {
            "offset": offset,
            "limit": limit
        }
        return self.process_http_request("getUpdates", params).get("result", [])

    def run(self):

        while True:
            updates = self.get_updates()
            if updates:
                self.process_updates(updates)
                self.updates = []

            # Check the server message status every 10 seconds
            self.check_server_message()
            time.sleep(10)

    def check_server_message(self):
        """
        Check the server message status and update the widget accordingly.
        """
        with self.lock:
            if self.server_msg['status'] == 'running':
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard(['Stop', 'Pause', 'Resume']))
            elif self.server_msg['status'] == 'paused':
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard(['Start', 'Resume']))
            else:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard(['Start']))

    def process_state(self, state):
        """
        Process the current state of the bot and update the widget accordingly.

        Args:
        state (int): The current state of the bot.
        """
        with self.lock:
            if state == 5:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard(
                    ['Help', 'Status', 'Balance', 'Transactions', 'Stellar', 'Trade', 'Analysis', 'Subscribe',
                     'Unsubscribe']))
            elif state == 6:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard([
                    'Help', 'Status', 'Balance', 'Transactions', 'Stellar', 'Trade', 'Analysis', 'Subscribe',
                    'Unsubscribe']))
                self.send_message(self.server_msg['chat_id'], "StellarBot is now in help mode.")

            elif state == 7:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard([
                    'Help', 'Status', 'Balance', 'Transactions', 'Stellar', 'Trade', 'Analysis', 'Subscribe',
                    'Unsubscribe']))
                self.send_message(self.server_msg['chat_id'], "StellarBot is now in analysis mode.")

            elif state == 8:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard([
                    'Help', 'Status', 'Balance', 'Transactions', 'Stellar', 'Trade', 'Analysis', 'Subscribe',
                    'Unsubscribe']))
                self.send_message(self.server_msg['chat_id'], "StellarBot is now in subscribe mode.")

            elif state == 9:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard([
                    'Help', 'Status', 'Balance', 'Transactions', 'Stellar', 'Trade', 'Analysis', 'Subscribe',
                    'Unsubscribe']))
                self.send_message(self.server_msg['chat_id'], "StellarBot is now in unsubscribe mode.")

            elif state == 10:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard([
                    'Help', 'Status', 'Balance', 'Transactions', 'Stellar', 'Trade', 'Analysis', 'Subscribe',
                    'Unsubscribe']))
                self.send_message(self.server_msg['chat_id'], "StellarBot is now in balance mode.")

            elif state == 11:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard([
                    'Help', 'Status', 'Balance', 'Transactions', 'Stellar', 'Trade', 'Analysis', 'Subscribe',
                    'Unsubscribe']))
                self.send_message(self.server_msg['chat_id'], "StellarBot is now in transactions mode.")

            elif state == 12:
                self.send_reply_keyboard(self.server_msg['chat_id'], create_keyboard([
                    'Help', 'Status', 'Balance', 'Transactions', 'Stellar', 'Trade', 'Analysis', 'Subscribe',
                    'Unsubscribe']))
                self.send_message(self.server_msg['chat_id'], "StellarBot is now in stellar mode.")

    def process_updates(self, updates):
        """
        Process incoming updates and trigger appropriate actions.

        Args:
        updates (list): A list of updates received from the Telegram bot.
        """
        for update in updates:
            if 'message' in update:
                self.process_message(update['message'])

    def screenshot(self):
        """
        Take a screenshot of the bot's interface and save it as a JPEG file.
        """
        self.send_action(self.server_msg['chat_id'], Actions.TYPING)
        params = {
            "chat_id": self.server_msg['chat_id'],
            "reply_to_message_id": self.server_msg['message_id'],
            "caption": "Here's a screenshot of StellarBot's interface:"
        }
        response = self.process_http_request("sendPhoto", params)
        photo_id = response.get("result", {})["photo"][-1]["file_id"]
        file_path = self.download_file(photo_id)
        save_screenshot(file_path)
        self.send_message(self.server_msg['chat_id'], "Screenshot saved as screenshot.jpg")
        os.remove(file_path)

    def download_file(self, photo_id):
        """
        Download a file from Telegram and save it locally.

        Args:
        photo_id (str): The ID of the photo file.
        Returns:
            str: The path where the file was saved.
            None: If the file download fails.
            """
        response = requests.get(f"https://api.telegram.org/file/bot{self.token}/{photo_id}")
        if response.status_code == 200:
            file_path = f"screenshot_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        else:
            return None

import json
import os
import time
from datetime import datetime
from enum import Enum
from threading import Lock, Thread

import pandas as pd
import pyautogui
import requests


class Actions(Enum):
    TYPING = 'typing'
    UPLOAD_PHOTO = 'upload_photo'
    UPLOAD_VIDEO = 'upload_video'
    UPLOAD_AUDIO = 'upload_audio'
    UPLOAD_DOCUMENT = 'upload_document'
    CHOOSE_STICKER = 'choose_sticker'
    RECORD_VIDEO = 'record_video'
    RECORD_AUDIO = 'record_audio'
    FIND_LOCATION = 'find_location'
    RECORD_VIDEO_NOTE = 'record_video_note'
    UPLOAD_VIDEO_NOTE = 'upload_video_note'


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

    def __init__(self, token: str, controller):

        self.commands = None
        self.lock = Lock()
        self.current_state = 0
        self.controller = controller.asset_pairs
        self.df_chat_info = pd.DataFrame(columns=['chat_id', 'status'])  # DataFrame for chat status
        self.server_msg = controller.server_msg
        self.chat_id = controller.chat_id

        self.token = token
        self.updates = []  # List to store incoming updates from the Telegram bot
        self.update_id = 0  # ID of the last received update
        self.logger = controller.logger
        self.logger.info("TelegramBot initialized")

        # Set the server message data
        self.server_msg['status'] = "stopped"
        self.server_msg['message'] = "StellarBot is not running."

        # Set up the HTTP client for making requests to the Telegram API
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

        # Set up the HTTP client for making requests to the Stellar network
        self.stellar_session = self.session
        self.stellar_session.headers.update({"Content-Type": "application/json"})
        self.stellar_session.headers.update({"X-User-Agent": "StellarBot"})
        self.command_handlers = {
            "/start": self.start_command,
            "/help": self.help_command,
            "/subscribe": self.subscribe_command,
            "/unsubscribe": self.unsubscribe_command,
            "/account": self.balance_command,
            # "/price": self.price_command,
            "/chart": self.chart_command,
            # "/pair": self.pair_command,
            # "/pair_status": self.pair_status_command,
            # "/pair_history": self.pair_history_command,
            # "/order": self.order_command,
            # "/order_status": self.order_status_command,
            "/order_history": self.order_history_command,
            # "/deposit": self.deposit_command,
            # "/withdraw": self.withdraw_command,
            # "/deposit_history": self.deposit_history_command,
            # "/withdraw_history": self.withdraw_history_command,

            "/report": self.report_command,
            "/analysis": self.analysis_command,
            "/news": self.news_command,
            "/trade": self.trade_command,
            "/history": self.history_command,
            "/settings": self.settings_command,
            "/exit": self.exit_command,
            "/about": self.about_command,
            "/stellar": self.stellar_command
        }
        self.server_msg = {
            "message": "",
            "status": "",
            "message_type": "",
            "action": "update_trade_signal",
            "chat_id": 0,
            "trade_signal": 0,
            "selected_strategy": "",
            "last_update": datetime.now(),
            "info": "",
            "error": "",
            "pair": ""
        }




        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()
        self.keep_running = True

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
        Params (dict): The parameters to be included in the request.

        Returns:
        dict: A dictionary containing the response data from the Telegram API.
        """
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        response = self.session.post(url, json=params)

        if response.status_code != 200:
            self.logger.error(f"Error processing HTTP request: {response.status_code} - {response.text}")
            return {}

        return response.json()

    def send_action(self, chat_id: int, action: Actions):
        """
        Send an action to a Telegram chat.
        Args:
        chat_id (int): The ID of the chat where the action will be sent.
        Action (Actions): The action to be performed.
        Data (dict, optional): Additional data to be included in the action request.

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
        Keyboard (list): The keyboard layout to be sent.
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

    def send_message(self, chat_id: int = None, message: str = None):
        """
        Send a message to a Telegram chat.

        Args:
        chat_id (int): The ID of the chat where the message will be sent.
        Message (str): The message to be sent.
        """

        if chat_id is None or message is None:
            return
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
        Photo_path (str): The path to the photo file.
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
        Audio_path (str): The path to the audio file.
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
        Document_path (str): The path to the document file.
        """
        self.send_action(chat_id=chat_id, action=Actions.UPLOAD_DOCUMENT)
        params = {
            "chat_id": chat_id,
            "document": open(document_path, "rb")
        }
        self.process_http_request("sendDocument", params)

    def get_updates(self, offset: int = 0, limit: int = 100) -> list:
        """
        Retrieve updates from the Telegram bot and process the information.

        Args:
        offset (int, optional): The offset for pagination. Default is 0.
        Limit (int, optional): The maximum number of updates to return. Defaults to 100.

        Returns:
        list: A list of updates.
        """
        try:
            # Ensure self.updates exists and has at least one update to avoid IndexError
            if self.updates:
                last_update_id = self.updates[0]['update_id'] + 1
                self.send_action(last_update_id, Actions.TYPING)
            else:
                self.send_action(offset, Actions.CHOOSE_STICKER)  # Use provided offset if no updates

            params = {
                "offset": offset,
                "limit": limit
            }

            response = self.process_http_request("getUpdates", params)

            # Check if the response is valid and contains the expected 'result' field
            if response and 'result' in response:
                res = response['result']

                if res:

                    self.chat_id = res[0]['message']['chat']['id']

                    # Update the self.updates list with the new updates
                    self.updates.extend(res)
                    self.updates.sort(key=lambda x: x['update_id'])

                    # Update the DataFrame with the new chat_id
                    self.update_chat_info(self.chat_id)
                    self.logger.info(f"Fetched {len(res)} updates.")

                    # Extract and return the updates
                    return res
                else:
                    self.logger.warning("No result in the response.")
                    return []
            else:
                self.logger.warning(f"Failed to fetch updates: {response}")
                return []

        except Exception as e:
            self.logger.error(f"Error in get_updates: {str(e)}", exc_info=True)
            return []

    def update_chat_info(self, chat_id):
        """
        Update the DataFrame with the chat_id and status.

        Args:
        chat_id (int): The chat ID to be updated.
        """
        # Check if the chat_id already exists in the DataFrame
        if chat_id not in self.df_chat_info['chat_id'].values:
            # Add a new row with the chat_id and default status 'idle'

            new_row = pd.DataFrame({'chat_id': [chat_id], 'status': ['idle']})
            self.df_chat_info = pd.concat([self.df_chat_info, new_row], ignore_index=True)


        else:
            # Optionally, update the status if needed (for example, setting it to 'active')
            self.df_chat_info.loc[self.df_chat_info['chat_id'] == chat_id, 'status'] = 'active'

    def run(self):
        while True:
            updates = self.get_updates()
            if updates:
                self.process_updates(updates)
                self.updates = []

                # Process the command in the chat
                command = updates[0]['message']['text'].lower()
                if command.startswith('/'):
                    self.process_command(command, updates[0]['message'])
                    self.save_server_msg()
            else:
                self.logger.warning("No updates received.")

            # Check the server message status every 10 seconds
            self.check_server_message()
            time.sleep(10)

    def check_server_message(self):
        """
        Check the server message status and update the widget accordingly.
        """
        with self.lock:
            if self.server_msg.get('status', '') == 'RUNNING':
                self.send_reply_keyboard(self.chat_id, create_keyboard(['Stop', 'Pause', 'Resume']))
            elif self.server_msg.get('status', '') == 'paused':
                self.send_reply_keyboard(self.chat_id, create_keyboard(['Start', 'Resume']))
            else:
                self.send_reply_keyboard(self.chat_id, create_keyboard(['Start']))

    def screenshot(self):
        """
        Take a screenshot of the bot's interface and save it as a JPEG file.
        """
        self.send_action(self.chat_id, Actions.TYPING)
        params = {
            "chat_id": self.chat_id,
            "reply_to_message_id": self.server_msg['message_id'],
            "caption": "Here's a screenshot of StellarBot's interface:"
        }
        response = self.process_http_request("sendPhoto", params)
        photo_id = response.get("result", {})["photo"][-1]["file_id"]
        file_path = self.download_file(photo_id)
        save_screenshot(file_path)
        self.send_message(self.chat_id, "Screenshot saved as screenshot.jpg")
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

    def process_command(self, command, message):

        for action, param in self.command_handlers.items():
            if command == action:
                self.send_action(self.chat_id, Actions.TYPING)
                self.logger.info(f"Processing command: {command}")
                self.execute_command(message)
                return

    def send_welcome_message(self, param):
        """
        Send a welcome message to the user.

        Args:
        param (dict): The parameters associated with the welcome message.
        """
        self.send_message(param, "Hello! StellarBot is here to help you manage your cryptocurrency accounts.")
        self.send_message(param, "Type /start to get started.")

    def save_server_msg(self):
        """
        Save the server message to a JSON file.
        """

        # Assuming self.server_msg contains a datetime object

        for key, value in self.server_msg.items():
            if isinstance(value, datetime):
                self.server_msg[key] = value.isoformat()

        with open("server_msg.json", "w") as fc:
            json.dump(str(self.server_msg), fc)

    def chat_states(self, state: int):

        if state == 1:
            self.send_message(self.chat_id, "StellarBot is now in trade mode.")

        elif state == 2:
            self.send_message(self.chat_id, "StellarBot is now in analysis mode.")

        elif state == 3:
            self.send_message(self.chat_id, "StellarBot is now in error mode.")

        elif state == 4:
            self.send_message(self.chat_id, "StellarBot is now in alert mode.")


        elif state == 23:  #Trade mode
            self.send_message(self.chat_id, "Trade mode is temporarily unavailable. Please try again later.")

    def trade_command(self):

        self.send_message(self.chat_id, "Select a cryptocurrency pair to trade.")
        self.send_reply_keyboard(self.chat_id, create_keyboard([
            self.controller.get_available_pairs()
        ]))

    def start_command(self):
        self.start()

    def pause_command(self):
        pass

    def resume_command(self):
        self.controller.start()

    def stop_command(self):
        self.stop()

    def status_command(self):
        self.send_message(self.chat_id, "StellarBot is currently in status:" + self.server_msg["status"])

    def balance_command(self):
        list_of_commands = "\n".join([f"{command} - {description}" for command, description in self.commands.items()])
        self.send_message(self.chat_id, "Here are the available commands for Balance:\n" + list_of_commands)

    def transactions_command(self):
        list_of_commands = "\n".join([f"{command} - {description}" for command, description in self.commands.items()])
        self.send_message(self.chat_id, "Here are the available commands for Transactions:\n" + list_of_commands)

    def stellar_command(self):

        list_of_commands = "\n".join([f"{command} - {description}" for command, description in self.commands.items()])
        self.send_message(self.chat_id, "Here are the available commands for StellarBot:\n" + list_of_commands)

    def analysis_command(self):
        pass

    def subscribe_command(self):
        pass

    def unsubscribe_command(self):
        pass

    def screenshot_command(self):
        self.screenshot()

    def help_command(self):
        self.send_message(self.chat_id,
                          "StellarBot is an AI-powered cryptocurrency management tool. Type /start to get started.")

    def report_command(self):
        pass

    def settings_command(self):
        pass

    def news_command(self):

        pass

    def history_command(self):
        pass

    def exit_command(self):
        pass

    def about_command(self):

        self.send_message(self.chat_id,
                          "StellarBot is an AI-powered cryptocurrency management tool. Type /start to get started.")

    def start(self):

        self.send_message(self.chat_id, "StellarBot is now in help mode.")
        self.chat_states(1)

    def stop(self):
        self.send_message(self.chat_id, "StellarBot is now in idle mode.")
        self.chat_states(2)

    def process_updates(self, updates):
        """
        Process incoming updates from Telegram.

        Args:
        updates (list): A list of updates received from Telegram.
        """
        for update in updates:
            server_msg = update.get("message", {})
            if "text" in self.server_msg:
                self.process_command(server_msg["text"], server_msg)

            if "callback_query" in self.server_msg:
                self.process_callback_query(self.server_msg["callback_query"])

                if self.server_msg["callback_query"] == "cancel":

                    self.send_message(self.chat_id, "Operation cancelled.")

    def process_callback_query(self, param):
        """
        Process incoming callback queries from Telegram.

        Args:
        param (dict): The parameters associated with the callback query.
        """
        data = param["data"]

        if data == "trade":
            self.trade_command()

        elif data == "/start":
            self.start_command()

        elif data == "/pause":
            self.pause_command()

        elif data == "/resume":
            self.resume_command()

        elif data == "/stop":
            self.stop_command()

        elif data == "/status":
            self.status_command()

        elif data == "/balance":
            self.balance_command()

        elif data == "/transactions":
            self.transactions_command()

        elif data == "/stellar":
            self.stellar_command()

        elif data == "/analysis":
            self.analysis_command()

        elif data == "/subscribe":
            self.subscribe_command()

        elif data == "/unsubscribe":
            self.unsubscribe_command()

        elif data == "/screenshot":
            self.screenshot_command()
        elif data=="/quotes":
            self.send_message(self.chat_id, self.get_quotes())
        elif data == "help":
            self.help_command()

    def get_quotes(self):
        """
        Fetch and return random quotes from an API.

        Returns:
            str: A randomly selected quote.
            None: If the API request fails.
        """
        try:
            response = requests.get("https://api.binance.us/v3/ticker/price?symbol=BTCUSDT")
            if response.status_code == 200:
                return response.json()["content"]
            else:
                self.logger.error(f"Failed to fetch quotes from API: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching quotes: {e}")
            return None

    def execute_command(self, message):
        """
        Execute a specific command based on the given parameters.

        Args:
        param (dict): The parameters associated with the command.
        Message (dict): The message containing the command.
        """
        command = message["text"].split()[0].lower()

        if command in self.command_handlers:
            self.command_handlers[command]()

        else:
            context = self.get_context(message)
            if context:
                self.send_message(message["chat"]["id"],
                                  f"I'm sorry, I didn't understand '{message['text']}'. Try '{context}' instead.")

    def get_context(self, message):
        """
        Determine the context of a given message.

        Args:
        message (dict): The message containing the command.

        Returns:
        str: The context of the message.
        None: If the context cannot be determined.
        """
        words = message["text"].split()
        if len(words) > 1:
            context = words[1]
            if context in self.command_handlers:
                return context
            else:
                return None

    def chart_command(self):
        """
        Display a chart of the cryptocurrency pair.
        """
        pair = self.server_msg["pair"]
        chart_url = self.controller.get_chart_url(pair)
        self.send_photo(self.chat_id, chart_url)

    def order_history_command(self):
        """
        Display the order history of the user.
        """
        orders = self.controller.get_order_history()
        if orders:
            self.send_message(self.chat_id, "Order history:")
            for order in orders:
                self.send_message(self.chat_id, f"{order['id']} - {order['price']} {order['pair']} - {order['side']}")
        else:
            self.send_message(self.chat_id, "No order history available.")


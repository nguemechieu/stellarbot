import time

from stellar_sdk import Server


class RiskManagement:
    def __init__(self, controller, asset, risk_threshold=0.5, monitor_interval=60):
        """
        Initializes the RiskManagement class to monitor and manage risk for a given asset.

        Parameters:
        - controller: The main controller object managing the bot.
        - asset (str): The asset to monitor (e.g., 'USDC').
        - risk_threshold (float): The percentage of the total balance to risk (e.g., 5 for 5%).
        - monitor_interval (int): How often to check the balance, in seconds (default is 60 seconds).
        """
        self.controller = controller
        self.asset = asset
        self.risk_threshold = risk_threshold
        self.monitor_interval = monitor_interval
        self.logger = controller.logger
        # Initialize the other necessary attributes
        self.balance = self._fetch_balance()
        self.total_balance = self._fetch_total_balance()
        self.last_checked = time.time()
        self.is_risk_exceeded = False

        # User-defined action to execute when the risk threshold is exceeded
        self.risk_action = None

        self.set_risk_action(self.controller.sell_asset_action)  # Set the action to sell the asset
        self.monitor()  # Start monitoring

    def _fetch_balance(self):
        """
        Fetches the balance of the specific asset to monitor.
        """
        try:
            balance = self.controller.get_balance(self.asset)
            self.logger.info(f"Fetched balance for {self.asset}: {balance}")
            return balance
        except Exception as e:
            self.logger.error(f"Error fetching balance for {self.asset}: {e}")
            return 0  # Return 0 if fetching balance fails

    def _fetch_total_balance(self):
        """
        Fetches the total balance of the account (all assets).
        """
        try:
            total_balance =self.controller.get_total_balance()  # Assuming this method exists
            self.logger.info(f"Fetched total balance: {total_balance}")
            return total_balance
        except Exception as e:
            self.logger.error(f"Error fetching total balance: {e}")
            return 0  # Return 0 if fetching total balance fails

    def set_risk_action(self, action):
        """
        Sets the user-defined action to be executed when the risk threshold is exceeded.

        Parameters:
        - action (callable): A function that will be executed when risk exceeds the threshold.
        """
        if callable(action):
            self.risk_action = action
            self.logger.info(f"Risk action set to: {action.__name__}")
        else:
            self.logger.error("Provided action is not callable.")
            raise ValueError("Action must be callable.")

    def check_risk(self):
        """
        Checks if the risk threshold has been exceeded by comparing the asset balance
        to the total balance and the defined risk threshold.

        Returns:
        - bool: True if the risk threshold is exceeded, False otherwise.
        """
        risk_percentage = (self.balance / self.total_balance) * 100

        if risk_percentage > self.risk_threshold:
            self.is_risk_exceeded = True
            self.logger.warning(f"Risk threshold exceeded: {risk_percentage}% > {self.risk_threshold}%")
            return True
        else:
            self.is_risk_exceeded = False
            return False

    def execute_risk_action(self):
        """
        Executes the user-defined action if the risk threshold is exceeded.
        """
        if self.risk_action and self.is_risk_exceeded:
            try:
                self.logger.info(f"Executing risk management action: {self.risk_action.__name__}")
                self.risk_action()
            except Exception as e:
                self.logger.error(f"Error executing risk action: {e}")
        elif not self.is_risk_exceeded:
            self.logger.info(f"Risk is within limits, no action needed.")
        else:
            self.logger.warning("No risk action defined.")

    def monitor(self):
        """
        Starts monitoring the asset balance and takes appropriate action if the risk threshold is exceeded.
        This method will repeatedly check the balance and execute the action at specified intervals.
        """
        self.logger.info(f"Started monitoring {self.asset} balance with risk threshold at {self.risk_threshold}%.")

        while True:
            current_time = time.time()

            # Check if it's time to monitor
            if current_time - self.last_checked >= self.monitor_interval:
                self.last_checked = current_time
                self.balance = self._fetch_balance()  # Update balance
                self.total_balance = self._fetch_total_balance()  # Update total balance

                if self.check_risk():
                    self.execute_risk_action()  # Execute the action if risk is exceeded

            time.sleep(self.monitor_interval)  # Wait before checking again

    def stop_monitoring(self):
        """
        Stops the monitoring process (typically used in multithreaded or long-running processes).
        """
        self.logger.info("Stopping risk management monitoring.")
        self.is_risk_exceeded = False


#
# # Example Usage

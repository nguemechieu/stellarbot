from unittest import TestCase
from unittest.mock import patch, MagicMock
from stellar_sdk import Keypair, Asset

from src.modules.classes.stellar_client import StellarClient


class TestStellarClient(TestCase):

    def setUp(self):
        # Example setup: create a mock StellarClient instance with dummy account ID and secret
        self.account_id = "GXXXXXX"
        self.secret_key = "SXXXXXX"
        self.mock_controller = MagicMock()  # Mock the controller object
        self.stellar_client = StellarClient(controller=self.mock_controller, account_id=self.account_id, secret_key=self.secret_key)

    @patch('src.stellar_client.Server')  # Mock the Server class in stellar_client
    def test_account_balance(self, MockServer):
        # Arrange
        mock_server_instance = MockServer.return_value
        mock_server_instance.accounts().account_id().call.return_value = {
            "balances": [{"balance": "100.0", "asset_type": "native"}]
        }

        # Act
        balance = self.stellar_client.get_balances()

        # Assert
        self.assertEqual(balance, "100.0")
        mock_server_instance.accounts().account_id().call.assert_called_once()

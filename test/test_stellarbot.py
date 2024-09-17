import os

import pytest
import tkinter
from unittest.mock import patch, MagicMock

from stellarbot import StellarBot

@pytest.fixture
def stellar_bot():
    with patch('stellarbot.DatabaseManager') as MockDatabaseManager:
        mock_db = MagicMock()
        MockDatabaseManager.return_value.db = mock_db
        bot = StellarBot()
        yield bot
        bot.destroy()

@pytest.mark.parametrize("param", ["Login", "CreateAccount", "Home", "About"], ids=["Login", "CreateAccount", "Home", "About"])
def test_show_pages(stellar_bot, param):
    # Act
    stellar_bot.show_pages(param)

    # Assert
    assert stellar_bot.title() == f"StellarBot@{param}"
    assert len(stellar_bot.winfo_children()) > 0

def test_delete_frame(stellar_bot):
    # Arrange
    frame = tkinter.Frame(stellar_bot)
    frame.pack()

    # Act
    stellar_bot.delete_frame()

    # Assert
    assert len(stellar_bot.winfo_children()) == 0

def test_exit():
    # Arrange
    with patch('os._exit') as mock_exit:
        bot = StellarBot()

        # Act
        bot.exit()

        # Assert
        mock_exit.assert_called_once_with(1)

def test_updateMe(stellar_bot):
    # Arrange
    with patch.object(stellar_bot, 'after') as mock_after:

        # Act
        stellar_bot.updateMe()

        # Assert
        mock_after.assert_called_once_with(1000, stellar_bot.updateMe)

@pytest.mark.parametrize("msg", ["Error occurred", "Invalid input"], ids=["ErrorOccurred", "InvalidInput"])
def test_show_error_message(stellar_bot, msg):
    # Act
    stellar_bot.show_error_message(msg)

    # Assert
    assert len(stellar_bot.winfo_children()) > 0
    message_widget = stellar_bot.winfo_children()[0]
    assert isinstance(message_widget, tkinter.Message)
    assert message_widget.cget("text") == msg
    assert message_widget.cget("bg") == 'red'
    assert message_widget.cget("fg") == 'white'

@pytest.mark.parametrize("system, expected", [
    ("Windows", "Windows"),
    ("Linux", "Linux"),
    ("Darwin", "macOS"),
    ("UnknownOS", "Unknown")
], ids=["Windows", "Linux", "macOS", "Unknown"])
def test_check_os(system, expected):
    # Arrange
    with patch('platform.system', return_value=system):

        # Act
        result = check_os()

        # Assert
        assert result == expected

def test_main_linux():
    # Arrange
    with patch('platform.system', return_value="Linux"), \
         patch('subprocess.Popen') as mock_popen, \
         patch('os.environ', {}), \
         patch('stellarbot.StellarBot') as MockStellarBot:

        # Act
        import stellarbot
        stellarbot.__name__ = "__main__"
        stellarbot.main()

        # Assert
        mock_popen.assert_any_call("Xvfb :99 -screen 0 1280x1024x24 &", shell=True)
        assert os.environ["DISPLAY"] == ":99"
        MockStellarBot.assert_called_once()

def test_main_windows():
    # Arrange
    with patch('platform.system', return_value="Windows"), \
         patch('os.environ', {}), \
         patch('stellarbot.StellarBot') as MockStellarBot:

        # Act
        import stellarbot
        stellarbot.__name__ = "__main__"
        stellarbot.main()

        # Assert
        assert os.environ["DISPLAY"] == ":0"
        MockStellarBot.assert_called_once()

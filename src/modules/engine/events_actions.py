from enum import Enum


class EventsActions(Enum):
    """Enum for events and actions."""

    LOGIN = "login"
    LOGOUT = "logout"
    SET_API_KEY = "set_api_key"
    SET_PREFERENCES = "set_preferences"
    START_BOT = "start_bot"
    CREATE_ACCOUNT = "create new account"

    START_STREAMING = "start_streaming"
    STOP_STREAMING = "stop_streaming"
    UPDATE_BALANCE = "update_balance"
    UPDATE_OFFERS = "update_offers"
    UPDATE_TRADE_HISTORY = "update_trade_history"
    UPDATE_EFFECTS = "update_effects"
    UPDATE_PORTFOLIO = "update_portfolio"
    UPDATE_TRADING_SIGNALS = "update_trading_signals"
    UPDATE_SERVER_MESSAGE = "update_server_message"
    EXECUTE_TRADING_STRATEGY = "execute_trading_strategy"
    STOP_BOT = "stop_bot"
    ERROR = "error"
    TRADE_SUCCESS = "trade_success"
    TRADE_FAILURE = "trade_failure"
    TRADE_UPDATE = "trade_update"
    ORDER_BOOK_UPDATE = "order_book_update"
    PRICE_UPDATE = "price_update"
    ORDER_UPDATE = "order_update"
    MARKET_UPDATE = "market_update"

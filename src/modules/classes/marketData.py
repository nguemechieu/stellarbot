import random

class MarketData:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_price(self) -> float:
        # Simulated price for the asset (In reality, this should fetch live data)
        return round(random.uniform(1.0, 100.0), 2)

    def get_volume(self) -> float:
        # Simulated volume data
        return round(random.uniform(100, 10000), 2)
    
    def get_candles(self, interval: str, start_date: str, end_date: str) -> list:
        return self._extracted_from_get_ohlcv_3(start_date)
    
    def get_ohlcv(self, interval: str, start_date: str, end_date: str) -> list:
        return self._extracted_from_get_ohlcv_3(start_date)

    # TODO Rename this here and in `get_candles` and `get_ohlcv`
    def _extracted_from_get_ohlcv_3(self, start_date):
        candles = []
        for i in range(100):
            open_price = self.get_price()
            high_price = open_price + random.uniform(0.01, 0.1)
            low_price = open_price - random.uniform(0.01, 0.1)
            close_price = open_price + random.uniform(0.01, 0.1)
            volume = self.get_volume()
            candles.append(
                (
                    f'{start_date} {str(i)}',
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                )
            )
        return candles

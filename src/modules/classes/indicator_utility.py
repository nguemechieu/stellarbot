import numpy as np
import pandas as pd


def generate_cmf_signal(signal_setting, ohclv_data):
    #  CMF strategy logic
    data = ohclv_data.copy()
    data['M'] = (data['high'] + data['low'] + data['close']) / 3
    data['N'] = (data['high'].shift(signal_setting['period']) + data['low'].shift(signal_setting['period']) + data['close'].shift(signal_setting['period'])) / 3
    data['CMF'] = (data['N'] - data['M']) / (data['M'].rolling(window=signal_setting['period']).mean()) * 100
    data['CMF_Signal'] = np.where(data['CMF'] < -signal_setting['overbought_threshold'], 1, np.where(data['CMF'] > signal_setting['oversold_threshold'], -1, 0))
    data['Position'] = data['CMF_Signal'].diff()
    return data[['close', 'M', 'N', 'CMF', 'CMF_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_willr_signal(signal_setting, ohclv_data):
    #  WILLR strategy logic
    data = ohclv_data.copy()
    data['TR'] = np.maximum(np.maximum(data['high'] - data['low'], abs(data['high'] - data['close'].shift(1))), abs(data['low'] - data['close'].shift(1)))
    data['ATR'] = data['TR'].rolling(window=signal_setting['period']).mean()
    data['+DM'] = np.maximum(data['high'] - data['high'].shift(1), 0)
    data['-DM'] = np.maximum(data['low'].shift(1) - data['low'], 0)
    data['+DI'] = data['+DM'].rolling(window=signal_setting['period']).sum() / data['ATR']
    data['-DI'] = data['-DM'].rolling(window=signal_setting['period']).sum() / data['ATR']
    data['WillR'] = 100 - (100 * data['+DI'] / (data['+DI'] + data['-DI']))
    data['WillR_Signal'] = np.where(data['WillR'] < -signal_setting['overbought_threshold'], 1, np.where(data['WillR'] > signal_setting['oversold_threshold'], -1, 0))
    data['Position'] = data['WillR_Signal'].diff()
    return data[['close', 'TR', 'ATR', '+DM', '-DM', '+DI', '-DI', 'WillR', 'WillR_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_stoch_signal(signal_setting, ohclv_data):
    #  Stochastic strategy logic
    data = ohclv_data.copy()
    data['K'] = ((data['high'] - data['close']) / (data['high'] - data['low'].rolling(window=signal_setting['period']).min())) * 100
    data['D'] = data['K'].rolling(window=signal_setting['period']).mean()
    data['Stochastic_Signal'] = np.where(data['D'] < signal_setting['oversold_threshold'], 1, np.where(data['D'] > signal_setting['overbought_threshold'], -1, 0))
    data['Position'] = data['Stochastic_Signal'].diff()
    return data[['close', 'K', 'D', 'Stochastic_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_sar_signal(signal_setting, ohclv_data):
    #  SAR strategy logic
    data = ohclv_data.copy()
    data['High_Low_P'] = (data['high'] + data['low']) / 2
    data['High_Low_R'] = data['High_Low_P'].rolling(window=signal_setting['period']).max()
    data['SAR'] = data['High_Low_R'] - (signal_setting['acceleration'] * (data['High_Low_R'] - data['Low']))
    data['Position'] = np.where(data['close'] > data['SAR'], 1, np.where(data['close'] < data['SAR'], -1, 0))
    return data[['close', 'High_Low_P', 'High_Low_R', 'SAR', 'Position']].tail(1).to_dict(orient='records')[0]
    pass

def generate_custom_indicator_signal( signal_setting, ohclv_data):
    #  Custom indicator strategy logic
    data = ohclv_data.copy()
    # Add custom indicator data to the dataframe here
    # Example: Calculate a custom indicator based on other indicators
    data['Custom_Indicator'] = data['close'] - data['open']  # Replace 'close' and 'open' with actual column names
    data['Custom_Indicator_Signal'] = np.where(data['Custom_Indicator'] > 0, 1, np.where(data['Custom_Indicator'] < 0, -1, 0))
    data['Position'] = data['Custom_Indicator_Signal'].diff()
    return data[['close', 'Custom_Indicator', 'Custom_Indicator_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass

def generate_atr_signal(signal_setting, ohclv_data):
    #  Average True Range strategy logic
    data = ohclv_data.copy()
    data['H-L'] = data['high'] - data['low']
    data['H-PC'] = np.abs(data['high'] - data['close'].shift())
    data['L-PC'] = np.abs(data['low'] - data['close'].shift())
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=signal_setting['period']).mean()
    data['ATR_Signal'] = np.where(data['close'] > data['close'].shift() + data['ATR'], 1, np.where(data['close'] < data['close'].shift() - data['ATR'], -1, 0))
    data['Position'] = data['ATR_Signal'].diff()
    return data[['close', 'H-L', 'H-PC', 'L-PC', 'TR', 'ATR', 'ATR_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def calculate_asset_volatility(ohclv_data: pd.DataFrame) -> pd.Series:
    """Calculate asset volatility."""
    # Calculate asset volatility
    asset_volatility = ohclv_data["close"].pct_change().rolling(window=20).std()
    return asset_volatility
    pass
def generate_dmi_signal(signal_setting, ohclv_data):
    #  DMI strategy logic
    data = ohclv_data.copy()
    data['+DM'] = np.maximum(data['high'] - data['high'].shift(1), 0)
    data['-DM'] = np.maximum(data['low'].shift(1) - data['low'], 0)
    data['+DI'] = data['+DM'].rolling(window=signal_setting['period']).sum() / data['+DM'].rolling(window=signal_setting['period']).sum().rolling(window=signal_setting['period']).mean()
    data['-DI'] = data['-DM'].rolling(window=signal_setting['period']).sum() / data['-DM'].rolling(window=signal_setting['period']).sum().rolling(window=signal_setting['period']).mean()
    data['DX'] = 100 * np.abs(data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI'])
    data['ADX'] = data['DX'].rolling(window=signal_setting['period']).mean()
    data['ADX_Signal'] = np.where(data['ADX'] < signal_setting['oversold_threshold'], 1, np.where(data['ADX'] > signal_setting['overbought_threshold'], -1, 0))
    data['Position'] = data['ADX_Signal'].diff()
    return data[['close', 'ADX', 'ADX_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_ichimoku_signal(signal_setting, ohclv_data):
    #  Ichimoku strategy logic
    data = ohclv_data.copy()
    data['Tenkan_Span'] = (data['high'].rolling(window=signal_setting['tenkan_period']).max() + data['low'].rolling(window=signal_setting['tenkan_period']).min()) / 2
    data['Kijun_Span'] = data['Tenkan_Span'].rolling(window=signal_setting['kijun_period']).mean()
    data['Senkou_A'] = ((data['Tenkan_Span'] + data['Kijun_Span']) / 2).shift(signal_setting['senkou_a_period'])
    data['Senkou_B'] = ((data['high'].rolling(window=signal_setting['senkou_b_period']).max() + data['low'].rolling(window=signal_setting['senkou_b_period']).min()) / 2).shift(signal_setting['senkou_b_period'])
    data['Chikou_Span'] = data['close'].shift(-signal_setting['chikou_span_period'])
    data['Conversion_Line'] = (data['Senkou_A'] + data['Senkou_B']) / 2
    data['Base_Line'] = (data['Tenkan_Span'] + data['Kijun_Span']) / 2
    data['Signal_Line'] = (data['Conversion_Line'] + data['Base_Line']) / 2
    data['Ichimoku_Signal'] = np.where(data['Conversion_Line'] > data['Signal_Line'], 1, np.where(data['Conversion_Line'] < data['Signal_Line'], -1, 0))
    data['Position'] = data['Ichimoku_Signal'].diff()
    return data[['close', 'Tenkan_Span', 'Kijun_Span', 'Senkou_A', 'Senkou_B', 'Chikou_Span', 'Conversion_Line', 'Base_Line', 'Signal_Line', 'Ichimoku_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_aroon_signal(signal_setting, ohclv_data):
    #  Aroon strategy logic
    data = ohclv_data.copy()
    data['Aroon_Up'] = 100 - (100 / (data['high'].rolling(window=signal_setting['period']).max() - data['low'].rolling(window=signal_setting['period']).min()).rolling(window=signal_setting['period']).mean())
    data['Aroon_Down'] = 100 - (100 / (data['high'].rolling(window=signal_setting['period']).max() - data['low'].rolling(window=signal_setting['period']).min()).rolling(window=signal_setting['period']).mean())
    data['Aroon_Signal'] = np.where(data['Aroon_Up'] > data['Aroon_Down'], 1, np.where(data['Aroon_Up'] < data['Aroon_Down'], -1, 0))
    data['Position'] = data['Aroon_Signal'].diff()
    return data[['close', 'Aroon_Up', 'Aroon_Down', 'Aroon_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_uo_signal(signal_setting, ohclv_data):
    #  UO strategy logic
    data = ohclv_data.copy()
    data['UO'] = ((data['high'] + data['low'] + data['close']) / 3) - data['close'].shift(signal_setting['period'])
    data['UO_Signal'] = np.where(data['UO'] > signal_setting['overbought_threshold'], 1, np.where(data['UO'] < signal_setting['oversold_threshold'], -1, 0))
    data['Position'] = data['UO_Signal'].diff()
    return data[['close', 'UO', 'UO_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_kdj_signal(signal_setting, ohclv_data):
    #  KDJ strategy logic
    data = ohclv_data.copy()
    data['RSV'] = (data['close'] - data['low'].rolling(window=signal_setting['period']).min()) / (data['high'].rolling(window=signal_setting['period']).max() - data['low'].rolling(window=signal_setting['period']).min()) * 100
    data['K'] = data['RSV'].ewm(span=signal_setting['k_period'], min_periods=signal_setting['k_period']).mean()
    data['D'] = data['K'].ewm(span=signal_setting['d_period'], min_periods=signal_setting['d_period']).mean()
    data['J'] = 3 * data['K'] - 2 * data['D']
    data['KDJ_Signal'] = np.where(data['J'] < signal_setting['overbought_threshold'], 1, np.where(data['J'] > signal_setting['oversold_threshold'], -1, 0))
    data['Position'] = data['KDJ_Signal'].diff()
    return data[['close', 'RSV', 'K', 'D', 'J', 'KDJ_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_ppo_signal(signal_setting, ohclv_data):
    #  PPO strategy logic
    data = ohclv_data.copy()
    data['SMA_fast'] = data['close'].rolling(window=signal_setting['fast_ema_period']).mean()
    data['SMA_slow'] = data['close'].rolling(window=signal_setting['slow_ema_period']).mean()
    data['PPO'] = ((data['SMA_fast'] - data['SMA_slow']) / data['SMA_slow']) * 100
    data['PPO_Signal'] = np.where(data['PPO'] < -signal_setting['overbought_threshold'], 1, np.where(data['PPO'] > signal_setting['oversold_threshold'], -1, 0))
    data['Position'] = data['PPO_Signal'].diff()
    return data[['close', 'SMA_fast', 'SMA_slow', 'PPO', 'PPO_Signal', 'Position']].tail(1).to_dict(orient='records')[0]


def generate_trix_signal(signal_setting, ohclv_data):
    #  TRIX strategy logic
    data = ohclv_data.copy()
    data['TR'] = np.maximum(np.maximum(data['high'] - data['low'], abs(data['high'] - data['close'].shift(1))), abs(data['low'] - data['close'].shift(1)))
    data['TR14'] = data['TR'].rolling(window=signal_setting['period']).mean()
    data['trix'] = (data['TR14'].shift(signal_setting['period'] - 1) / data['TR14']) * -100
    data['Trix_Signal'] = np.where(data['trix'] < -signal_setting['overbought_threshold'], 1, np.where(data['trix'] > signal_setting['oversold_threshold'], -1, 0))
    data['Position'] = data['Trix_Signal'].diff()
    return data[['close', 'TR', 'TR14', 'trix', 'Trix_Signal', 'Position']].tail(1).to_dict(orient='records')[0]
    pass


def generate_bbands_signal(signal_setting, ohclv_data):
    #  Bollinger Bands strategy logic
    data = ohclv_data.copy()
    data['Middle_Band'] = data['close'].rolling(window=signal_setting['bbands_period']).mean()
    data['Upper_Band'] = data['Middle_Band'] + (signal_setting['bbands_std_dev'] * data['close'].rolling(window=signal_setting['bbands_period']).std())
    data['Lower_Band'] = data['Middle_Band'] - (signal_setting['bbands_std_dev'] * data['close'].rolling(window=signal_setting['bbands_period']).std())
    data['Bollinger_Band_Signal'] = np.where(data['close'] < data['Lower_Band'], 1, np.where(data['close'] > data['Upper_Band'], -1, 0))
    data['Position'] = data['Bollinger_Band_Signal'].diff()
    return data[['close', 'Middle_Band', 'Upper_Band', 'Lower_Band', 'Bollinger_Band_Signal', 'Position']].tail(1).to_dict(orient='records')[0]


def generate_ema_signal(signal_setting, ohclv_data):
    #  EMA strategy logic
    data = ohclv_data.copy()
    data['EMA'] = data['close'].ewm(span=signal_setting['period'], min_periods=signal_setting['period']).mean()
    data['EMA_Signal'] = np.where(data['close'] > data['EMA'], 1, np.where(data['close'] < data['EMA'], -1, 0))
    data['Position'] = data['EMA_Signal'].diff()
    return data[['close', 'EMA', 'EMA_Signal', 'Position']].tail(1).to_dict(orient='records')[0]


def generate_adx_signal(signal_setting, ohclv_data):
    #  ADX strategy logic
    data = ohclv_data.copy()
    data['true_range'] = np.abs(data['high'] - data['low'])
    data['plus_dm'] = np.where(data['high'].diff() > data['low'].diff(), data['high'] - data['high'].shift(1), 0)
    data['minus_dm'] = np.where(data['low'].diff() > data['high'].diff(), 0, data['low'] - data['low'].shift(1))
    data['dx'] = 100 * (np.abs(data['plus_dm']) + np.abs(data['minus_dm'])) / data['true_range']
    data['adx'] = data['dx'].ewm(span=signal_setting['period'], min_periods=signal_setting['period']).mean()
    data['ADX_Signal'] = np.where(data['adx'] < signal_setting['overbought_threshold'], 1, np.where(data['adx'] > signal_setting['oversold_threshold'], -1, 0))
    data['Position'] = data['ADX_Signal'].diff()
    return data[['close', 'true_range', 'plus_dm','minus_dm', 'dx', 'adx', 'ADX_Signal', 'Position']].tail(1).to_dict(orient='records')[0]


def generate_rsi_signal(signal_setting, ohclv_data):
    #  RSI strategy logic
    data = ohclv_data.copy()
    data['delta'] = data['close'].diff()
    data['gain'] = np.where(data['delta'] > 0, data['delta'], 0)
    data['loss'] = np.where(data['delta'] < 0, abs(data['delta']), 0)
    data['avg_gain'] = data['gain'].ewm(span=signal_setting['period'], min_periods=signal_setting['period']).mean()
    data['avg_loss'] = data['loss'].ewm(span=signal_setting['period'], min_periods=signal_setting['period']).mean()
    data['rsi'] = 100 - (100 / (1 + (data['avg_gain'] / data['avg_loss'])))
    data['RSI_Signal'] = np.where(data['rsi'] < signal_setting['overbought_threshold'], 1, np.where(data['rsi'] > signal_setting['oversold_threshold'], -1, 0))
    data['Position'] = data['RSI_Signal'].diff()
    return data[['close', 'delta', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rsi', 'RSI_Signal', 'Position']].tail(1).to_dict(orient='records')[0]


def generate_macd_signal(signal_setting, ohclv_data):
    #  MACD strategy logic
    data = ohclv_data.copy()
    data['EMA_fast'] = data['close'].ewm(span=signal_setting['fast_ema_period'], min_periods=signal_setting['fast_ema_period']).mean()
    data['EMA_slow'] = data['close'].ewm(span=signal_setting['slow_ema_period'], min_periods=signal_setting['slow_ema_period']).mean()
    data['MACD'] = data['EMA_fast'] - data['EMA_slow']
    data['Signal'] = data['MACD'].ewm(span=signal_setting['signal_ema_period'], min_periods=signal_setting['signal_ema_period']).mean()

    data['MACD_Signal'] = np.where(data['MACD'] > data['Signal'], 1, np.where(data['MACD'] < data['Signal'], -1, 0))
    data['Position'] = data['MACD_Signal'].diff()
    return data[['close', 'EMA_fast', 'EMA_slow', 'MACD', 'Signal', 'MACD_Signal', 'Position']].tail(1).to_dict(orient='records')[0]


def generate_bollinger_bands_signal(signal_settings, ohclv_data):
    #  Bollinger Bands strategy logic
    data = ohclv_data.copy()
    data['Middle_Band'] = data['close'].rolling(window=signal_settings['bbands_period']).mean()
    data['Upper_Band'] = data['Middle_Band'] + (signal_settings['bbands_std_dev'] * data['close'].rolling(window=signal_settings['bbands_period']).std())
    data['Lower_Band'] = data['Middle_Band'] - (signal_settings['bbands_std_dev'] * data['close'].rolling(window=signal_settings['bbands_period']).std())
    data['Bollinger_Band_Signal'] = np.where(data['close'] < data['Lower_Band'], 1, np.where(data['close'] > data['Upper_Band'], -1, 0))
    data['Position'] = data['Bollinger_Band_Signal'].diff()
    return data[['close', 'Middle_Band', 'Upper_Band', 'Lower_Band', 'Bollinger_Band_Signal', 'Position']].tail(1).to_dict(orient='records')[0]


def generate_sma_crossover_signal(params2, ohclv_data):
    #  SMA Crossover strategy logic
    data = ohclv_data.copy()
    data['SMA_short'] = data['close'].rolling(window=params2['short_window']).mean()
    data['SMA_long'] = data['close'].rolling(window=params2['long_window']).mean()
    data['Signal'] = np.where(data['SMA_short'] > data['SMA_long'], 1, 0)
    data['Position'] = data['Signal'].diff()
    return data[['close', 'SMA_short', 'SMA_long', 'Signal', 'Position']].tail(1).to_dict(orient='records')[0]


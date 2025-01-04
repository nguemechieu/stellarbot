import logging
import os
from datetime import datetime, timedelta
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(filename='ui_utility.log', level=logging.INFO)

def create_file(file_path, content):
    """
    Creates a new file with the given content.

    Args:
    - file_path (str): The path where the file will be created.
    - content (str): The content to be written to the file.
    """
    with open(file_path, "w") as f:
        f.write(content)
        logger.info(f"Created file: {file_path}")
        file_size = os.path.getsize(file_path)
        logger.info(f"File size: {file_size} bytes")
        f.close()


def open_file(file_path):
    """
    Opens the file located at the given path in a default text editor.

    Args:
    - file_path (str): The path of the file to be opened.
    """
    os.startfile(file_path)
    logger.info(f"Opened file: {file_path}")
    logger.info(f"File opened in default text editor")


def delete_file(file_path):
    """
    Deletes the file located at the given path.

    Args:
    - file_path (str): The path of the file to be deleted.
    """
    os.remove(file_path)
    logger.info(f"Deleted file: {file_path}")




def screen_shoot(file_path):
    """
    Takes a screenshot of the current screen and saves it to the specified file path.

    Args:
    - file_path (str): The path where the screenshot will be saved.
    """
    import pyautogui
    screen = pyautogui.screenshot()
    screen.save(file_path)
    logger.info(f"Saved screenshot to: {file_path}")
    logger.info(f"Screenshot saved as JPEG")


def exit_program():
    """
    Exits the program gracefully.
    """
    logger.info("Exiting program")
    exit(0)




def print_file_content(file_path):
    """
    Prints the content of the file located at the given path.

    Args:
    - file_path (str): The path of the file to be printed.
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
            logger.info(f"File content: {content}")
            f.close()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")



def show_screen_shoot(file_path):
    """
    Shows the screenshot saved at the given file path in a default image viewer.

    Args:
    - file_path (str): The path of the screenshot to be shown.
    """
    os.startfile(file_path)
    logger.info(f"Opened screenshot: {file_path}")
    logger.info(f"Screenshot opened in default image viewer")


def search_file(directory_path, search_term):
    """
    Searches for files in the specified directory and its subdirectories that contain the search term.

    Args:
    - directory_path (str): The path of the directory to be searched.
    - search_term (str): The term to be searched for in the files.
    """
    import glob
    file_paths = glob.glob(f"{directory_path}/**/*.txt", recursive=True)
    matching_files = [path for path in file_paths if search_term in open(path, "r").read()]
    logger.info(f"Found {len(matching_files)} matching files in {directory_path}")
    for path in matching_files:
        logger.info(f"Matching file: {path}")








def gennerate_market_annalysis(asset_info_df, market_data_df):
    """
    Generates a market analysis report based on the provided asset information and market data.

    Args:
    - asset_info_df (pd.DataFrame): A DataFrame containing asset information.
    - market_data_df (pd.DataFrame): A DataFrame containing market data.
    """
    import pandas as pd
    from datetime import datetime, timedelta

    # Filter market data based on the last 24 hours
    current_time = datetime.now()
    start_time = current_time - timedelta(hours=24)
    market_data_df = market_data_df[market_data_df['timestamp'] >= start_time]

    # Calculate the daily average price and volume for each asset
    daily_average_price_df = market_data_df.groupby(['asset_code', 'timestamp'])['price'].mean().reset_index()
    daily_average_volume_df = market_data_df.groupby(['asset_code', 'timestamp'])['volume'].sum().reset_index()
    daily_average_df = pd.merge(daily_average_price_df, daily_average_volume_df, on=['asset_code', 'timestamp'])
    daily_average_df['average_price'] = daily_average_df['price'] / daily_average_df['volume']
    daily_average_df = daily_average_df.drop(columns=['price', 'volume'])
    daily_average_df = daily_average_df.rename(columns={'average_price': 'daily_average_price'})

    # Calculate the weekly average price and volume for each asset
    weekly_average_price_df = market_data_df.groupby(['asset_code', pd.Grouper(key='timestamp', freq='7D')])['price'].mean().reset_index()
    weekly_average_volume_df = market_data_df.groupby(['asset_code', pd.Grouper(key='timestamp', freq='7D')])['volume'].sum().reset_index()
    weekly_average_df = pd.merge(weekly_average_price_df, weekly_average_volume_df, on=['asset_code', 'timestamp'])
    weekly_average_df['average_price'] = weekly_average_df['price'] / weekly_average_df['volume']
    weekly_average_df = weekly_average_df.drop(columns=['price', 'volume'])
    weekly_average_df = weekly_average_df.rename(columns={'average_price': 'weekly_average_price'})

    # Calculate the monthly average price and volume for each asset
    monthly_average_price_df = market_data_df.groupby(['asset_code', pd.Grouper(key='timestamp', freq='1M')])['price'].mean().reset_index()
    monthly_average_volume_df = market_data_df.groupby(['asset_code', pd.Grouper(key='timestamp', freq='1M')])['volume'].sum().reset_index()
    monthly_average_df = pd.merge(monthly_average_price_df, monthly_average_volume_df, on=['asset_code', 'timestamp'])
    monthly_average_df['average_price'] = monthly_average_df['price'] / monthly_average_df['volume']
    monthly_average_df = monthly_average_df.drop(columns=['price', 'volume'])
    monthly_average_df = monthly_average_df.rename(columns={'average_price': 'monthly_average_price'})

    # Merge daily, weekly, and monthly averages into a single DataFrame
    market_analysis_df = pd.merge(asset_info_df, daily_average_df, on='asset_code', how='left')
    market_analysis_df = pd.merge(market_analysis_df, weekly_average_df, on=['asset_code', 'timestamp'], how='left')
    market_analysis_df = pd.merge(market_analysis_df, monthly_average_df, on=['asset_code', 'timestamp'], how='left')

    # Calculate the percentage change in daily average price
    market_analysis_df['daily_price_change'] = (market_analysis_df['daily_average_price'] - market_analysis_df['previous_daily_average_price']) / market_analysis_df['previous_daily_average_price'] * 100

    # Calculate the percentage change in weekly average price
    market_analysis_df['weekly_price_change'] = (market_analysis_df['weekly_average_price'] - market_analysis_df['previous_weekly_average_price']) / market_analysis_df['previous_weekly_average_price'] * 100

    # Calculate the percentage change in monthly average price
    market_analysis_df['monthly_price_change'] = (market_analysis_df['monthly_average_price'] - market_analysis_df['previous_monthly_average_price']) / market_analysis_df['previous_monthly_average_price'] * 100

    # Generate the market analysis report
    report_path = "market_analysis_report.csv"
    market_analysis_df.to_csv(report_path, index=False)

    logger.info(f"Market analysis report generated: {report_path}")




# Install the missing package 'openpyxl' if you haven't
# pip install openpyxl

# Sample function that uses .corr() to generate correlation matrix
def generate_market_analysis_report(market_data_):
    """
    Generates a market analysis report based on the provided market data.

    Args:
    - market_data_df (pd.DataFrame): A DataFrame containing market data.

    Returns:
    - str: The path to the generated market analysis report.
    """
    # Calculate correlation matrix (ensure to only consider numeric columns)
    correlation_matrix = market_data_.corr(numeric_only=True)

    # Example of saving the correlation matrix to Excel (ensuring openpyxl is installed)
    report_path2 = "market_analysis_report.xlsx"
    with pd.ExcelWriter(report_path2, engine='openpyxl') as writer:
        correlation_matrix.to_excel(writer, sheet_name="Correlation Matrix")
        market_data_.to_excel(writer, sheet_name="Market Data")

    logger.info(f"Market analysis report generated: {report_path2}")
    return report_path2

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample market data generation (to test the function)
def create_random_market_data(param):
    """
    Generates random market data based on the provided parameter.

    Args:
    - param (int): The number of rows for the generated market data.

    Returns:
    - pd.DataFrame: A DataFrame containing random market data.
    """
    # Generate random prices
    prices = np.random.normal(100, 10, param)

    # Generate random timestamps for the past 24 hours
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(param)]

    # Create a DataFrame with random asset codes and timestamps
    _market_data_df = pd.DataFrame({
        "symbol": np.random.choice([
            "XLM", "BTC", "BTCLN", "ETH", "ADA", "LTC", "XRP", "BCH", "BSV",
            "EOS", "TRX", "SOL", "NEO", "IOTA", "LINK", "DASH", "ATOM"
        ], param),
        "timestamp": timestamps,
        "price": prices
    })

    return _market_data_df


# Test the function
market_data_df = create_random_market_data(1000)
generate_market_analysis_report(market_data_df)



def analyze_portfolio_performance(portfolio_data, market_data):
    """
    Analyzes the performance of a portfolio based on the provided market data.

    Args:
    - portfolio_data (pd.DataFrame): A DataFrame containing portfolio information.
    - market_data (pd.DataFrame): A DataFrame containing market data.
    """
    import pandas as pd
    from datetime import datetime, timedelta

    # Filter market data based on the last 24 hours
    current_time = datetime.now()
    start_time = current_time - timedelta(hours=24)
    market_data1 = market_data[market_data['timestamp'] >= start_time]

    # Calculate the daily portfolio value for each asset
    portfolio_value_df = pd.merge(portfolio_data, market_data1, on=['asset_code', 'timestamp'], how='inner')
    portfolio_value_df['daily_portfolio_value'] = portfolio_value_df['quantity'] * portfolio_value_df['price']

    # Calculate the total daily portfolio value
    total_daily_portfolio_value_df = portfolio_value_df.groupby('timestamp')['daily_portfolio_value'].sum().reset_index()
    total_daily_portfolio_value_df = total_daily_portfolio_value_df.rename(columns={'daily_portfolio_value': 'total_daily_portfolio_value'})

    # Calculate the percentage change in total daily portfolio value
    total_daily_portfolio_value_df['previous_total_daily_portfolio_value'] = total_daily_portfolio_value_df['total_daily_portfolio_value'].shift(1)
    total_daily_portfolio_value_df['daily_portfolio_value_change'] = (
            (total_daily_portfolio_value_df['total_daily_portfolio_value'] - total_daily_portfolio_value_df['previous_total_daily_portfolio_value'])
            / total_daily_portfolio_value_df['previous_total_daily_portfolio_value'] * 100
    )

    # Generate the portfolio performance report
    report_path_ = "portfolio_performance_report.csv"
    total_daily_portfolio_value_df.to_csv(report_path_, index=False)

    logger.info(f"Portfolio performance report generated: {report_path_}")


def simulate_trading_strategy(portfolio_df_, market_data_df_, trading_strategy):
    """
    Simulates a trading strategy based on the provided market data and trading strategy parameters.

    Args:
    - portfolio_df (pd.DataFrame): A DataFrame containing portfolio information.
    - market_data_df (pd.DataFrame): A DataFrame containing market data.
    - trading_strategy (dict): A dictionary containing trading strategy parameters.
    """
    # Filter market data based on the last 24 hours
    current_time = datetime.now()
    start_time = current_time - timedelta(hours=24)
    market_data_df_['timestamp'] = pd.to_datetime(market_data_df_['timestamp'])
    market_data_df_ = market_data_df_[market_data_df_['timestamp'] >= start_time]

    # Calculate the daily portfolio value for each asset based on the trading strategy
    portfolio_value_df = pd.merge(portfolio_df_, market_data_df_, on=['asset_code', 'timestamp'], how='inner')
    portfolio_value_df['trading_strategy_value'] = portfolio_value_df['quantity'] * portfolio_value_df['price'] * (1 + trading_strategy['trading_percentage'])

    # Calculate the total daily portfolio value based on the trading strategy
    total_daily_portfolio_value_df = portfolio_value_df.groupby('timestamp')['trading_strategy_value'].sum().reset_index()
    total_daily_portfolio_value_df = total_daily_portfolio_value_df.rename(columns={'trading_strategy_value': 'total_daily_portfolio_value'})

    # Calculate the percentage change in total daily portfolio value based on the trading strategy
    total_daily_portfolio_value_df['previous_total_daily_portfolio_value'] = total_daily_portfolio_value_df['total_daily_portfolio_value'].shift(1)
    total_daily_portfolio_value_df['trading_strategy_value_change'] = (
            (total_daily_portfolio_value_df['total_daily_portfolio_value'] - total_daily_portfolio_value_df['previous_total_daily_portfolio_value'])
            / total_daily_portfolio_value_df['previous_total_daily_portfolio_value'] * 100
    )

    # Generate the trading strategy report
    report_path1 = "trading_strategy_report.csv"
    total_daily_portfolio_value_df.to_csv(report_path1, index=False)

    logger.info(f"Trading strategy report generated: {report_path1}")

    return report_path1


def analyze_correlation_matrix(market_data, target_column):
    """
    Analyzes the correlation matrix of the provided market data and target column.

    Args:
    - market_data_df (pd.DataFrame): A DataFrame containing market data.
    - target_column (str): The name of the target column.
    """


    # Calculate the correlation matrix
    correlation_matrix = market_data.corr()

    # Create a heatmap
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
    plt.title(f"Correlation Matrix for {target_column}")
    plt.savefig("correlation_matrix.png")

    logger.info(f"Correlation matrix report generated: correlation_matrix.png")


def analyze_time_series_data(time_series_data, time_series_column, compare_data=None):
    """
    Analyzes the time series data of the provided market data and time series column.
    Optionally compares the time series with another time series.

    Args:
    - time_series_data (pd.Series): A Series containing the time series data to be analyzed.
    - time_series_column (str): The name of the time series column (for logging purposes).
    - compare_data (pd.Series): An optional second time series to compare with.
    """
    # Calculate the mean, median, and standard deviation of the time series column
    mean = time_series_data.mean()
    median = time_series_data.median()
    std_dev = time_series_data.std()

    # Create a histogram of the time series data
    plt.figure(figsize=(10, 6))  # Set figure size for better readability
    plt.hist(time_series_data, bins=50, color='skyblue', edgecolor='black', alpha=0.7, label=f'{time_series_column}')

    if compare_data is not None:
        plt.hist(compare_data, bins=50, color='orange', edgecolor='black', alpha=0.5, label='Market Data')  # Compare with another series

    plt.axvline(mean, color='red', label='Mean', linestyle='dashed', linewidth=2)
    plt.axvline(median, color='green', label='Median', linestyle='dashed', linewidth=2)
    plt.axvline(mean + std_dev, color='orange', label='Mean + Std. Dev.', linestyle='dashed', linewidth=2)
    plt.axvline(mean - std_dev, color='orange', label='Mean - Std. Dev.', linestyle='dashed', linewidth=2)

    # Adding labels and title
    plt.title(f"Time Series Analysis for {time_series_column}")
    plt.xlabel(f"{time_series_column} Values")
    plt.ylabel("Frequency")
    plt.legend()

    # Save the plot as a PNG image
    plot_path = "time_series_analysis_comparison.png" if compare_data is not None else "time_series_analysis.png"
    plt.savefig(plot_path)
    plt.close()  # Close the plot to avoid overlap

    # Log the report generation
    logger.info(f"Time series analysis report generated: {plot_path}")



def generate_portfolio_report(portfolio):
    """
    Generates a portfolio report based on the provided portfolio DataFrame.

    Args:
    - portfolio_df (pd.DataFrame): A DataFrame containing portfolio information.
    """
    portfolio_value_df = portfolio.groupby('asset_code')['quantity', 'price'].sum().reset_index()
    portfolio_value_df['total_value'] = portfolio_value_df['quantity'] * portfolio_value_df['price']
    portfolio_value_df = portfolio_value_df.rename(columns={'quantity': 'Total Quantity', 'price': 'Average Price'})

    logger.info("Portfolio report generated:")
    logger.info(portfolio_value_df)


def get_random_portfolio_data(param):
    """
    Generates random portfolio data based on the provided parameter.

    Args:
    - param (int): The number of rows for the generated portfolio data.

    Returns:
    - pd.DataFrame: A DataFrame containing random portfolio data.
    """
    import numpy as np

    # Generate random asset codes
    asset_codes = np.random.choice([  "XLM/USDC",
                                      "BTC/USD",
                                      "ETH/USD",
                                      "LTC/USD",
                                      "ADA/USD",
                                      "BCH/USD"], param)

    # Generate random quantities
    quantities = np.random.randint(1, 1000, param)

    # Create a DataFrame with random asset codes and quantities
    portfolio_df = pd.DataFrame({
        "symbol": asset_codes,
        "quantity": quantities,
        "price": np.random.normal(1000, 10, param)  # Placeholder for price data, actual prices will be calculated later
    })

    return portfolio_df

def generate_market_analysis_report(random_market_data_):
    """
    Generates a market analysis report based on the provided market data.

    Args:
    - market_data_df (pd.DataFrame): A DataFrame containing market data.

    Returns:
    - str: The path to the generated market analysis report.
    """

    # Constants for calculations
    sma_period = 5
    rsi_period = 14
    atr_period = 14

    # Step 1: Calculate technical indicators
    random_market_data_['SMA'] = random_market_data_['price'].rolling(window=sma_period).mean()

    # Step 2: Calculate returns
    random_market_data_['returns'] = random_market_data_['price'].pct_change()

    # Step 3: Calculate trading signals
    trading_signals_df = generate_trading_signals(random_market_data_)

    # Step 4: Calculate portfolio-related metrics
    sharpe_ratio = random_market_data_['returns'].mean() / random_market_data_['returns'].std() * np.sqrt(252)

    max_drawdown = random_market_data_['returns'].rolling(window=len(random_market_data_)).min() - random_market_data_['returns']
    max_drawdown = max_drawdown.min()

    total_portfolio_value = random_market_data_['price'].iloc[-1] * trading_signals_df['trading_signal'].sum()

    portfolio_returns = (total_portfolio_value - random_market_data_['price'].iloc[0]) / random_market_data_['price'].iloc[0] * 100
    annualized_returns = portfolio_returns * np.sqrt(252)

    # Step 5: Generate and save market analysis reports
    # Report for Market Data and Trading Signals (Excel)
    report_path2 = "market_analysis_report.xlsx"
    with pd.ExcelWriter(report_path2) as writer:
        random_market_data_.to_excel(writer, sheet_name="Market Data")
        trading_signals_df.to_excel(writer, sheet_name="Trading Signals")
        portfolio_returns_df = pd.DataFrame({
            "Portfolio Returns": [portfolio_returns],
            "Annualized Returns": [annualized_returns],
            "Sharpe Ratio": [sharpe_ratio],
            "Max Drawdown": [max_drawdown],
            "Total Portfolio Value": [total_portfolio_value]
            }, index=[0])
        portfolio_returns_df.to_excel(writer, sheet_name="Portfolio Metrics")
        print(f"Market analysis report generated: {report_path2}")
    logger.info(f"Market analysis report generated: {report_path2}")

    # Generate random portfolio data for demonstration purposes
    portfolio_dat = get_random_portfolio_data(1000)
    portfolio_dat['trading_signal'] = trading_signals_df['trading_signal'].shift(1)

    # Report for Portfolio Data (CSV)
    report_path1 = "market_analysis_report.csv"
    portfolio_dat.to_csv(report_path1, index=False)
    logger.info(f"Market analysis report generated: {report_path1}")

    return report_path1


def rsi_calc(param, period):
    """
    Calculates the relative strength index (RSI) for a given period.

    Args:
    - param (pd.DataFrame): The DataFrame containing market data.
    - period (int): The period for calculating RSI.

    Returns:

    - pd.DataFrame: A DataFrame containing the RSI values for each timestamp.
    """
    delta = market_data_df['price'].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_gain = up.ewm(com=period - 1).mean()
    avg_loss = down.ewm(com=period - 1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi



def generate_trading_signals(candle_data):
    """

    Generates trading signals based on the provided market data.

    Args:
    - market_data_df (pd.DataFrame): A DataFrame containing market data.

    Returns:
    - pd.DataFrame: A DataFrame containing trading signals.
    """
    #First validate the input DataFrame
    received_data = candle_data.dropna()  # Drop any rows with missing values
    drop_duplicates = received_data.drop_duplicates(subset=['timestamp'])  # Drop any duplicate timestamps
    if len(drop_duplicates)!= len(received_data):
        raise ValueError("Duplicate timestamps found in the DataFrame")

    #remove any rows with NaN or infinite values in the price column
    received_data = received_data[~received_data['price'].isnull()]
    received_data = received_data[~received_data['price'].isin([np.inf, -np.inf])]



    if not isinstance(received_data, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    if 'price' not in received_data.columns:
        raise ValueError("DataFrame must contain a 'price' column")
    if 'timestamp' not in received_data.columns:
        raise ValueError("DataFrame must contain a 'timestamp' column")

    if 'RSI' in received_data.columns:
        raise ValueError("DataFrame must not contain an 'RSI' column")
    if 'trading_signal' in received_data.columns:
        raise ValueError("DataFrame must not contain a 'trading_signal' column")




    # Implement trading logic based on SMA and RSI

    #Remove SMA and RSI columns for further calculations
    received_data = received_data[['symbol','timestamp', 'price']]
    received_data['trading_signal'] = 0  # Initialize trading signals with 0s


    trading_signals_df = received_data
    trading_signals_df['SMA'] = trading_signals_df['price'].rolling(window=5).mean()
    trading_signals_df['RSI'] = trading_signals_df['price']
    trading_signals_df['RSI'] = rsi_calc(trading_signals_df['price'], period=14)
    trading_signals_df['trading_signal'] = np.where(trading_signals_df['SMA'] > trading_signals_df['RSI'], 1, 0)

    return trading_signals_df




def create_random_portfolio_data(param):
    """
    Generates random portfolio data based on the provided parameter.

    Args:
    - param (int): The number of rows for the generated portfolio data.

    Returns:
    - pd.DataFrame: A DataFrame containing random portfolio data.
    """
    # Generate random asset codes
    asset_codes = np.random.choice([
        "XLM/USDC",
        "BTC/USD",
        "ETH/USD",
        "LTC/USD",
        "ADA/USD",
        "BCH/USD"
    ], param)

    # Generate random timestamps for the past 24 hours
    timestamps = [datetime.now().timestamp() - timedelta(hours=i).total_seconds() for i in range(param)]

    # Generate random quantities (assume between 1 and 100 for each asset)


    # Create a DataFrame
    portfolio_ = pd.DataFrame({
        "symbol": asset_codes,
        "timestamp": timestamps,

        "price": np.random.uniform(low=500, high=1000, size=param)  # Random prices between $500 and $1000 for each asset code
    })

    return portfolio_


def portfolio_performance_metrics(portfolio_trading_signals_):
    """
    Calculates portfolio performance metrics based on the provided portfolio trading signals.

    Args:
    - portfolio_trading_signals_ (pd.DataFrame): A DataFrame containing portfolio trading signals.

    Returns:
    - dict: A dictionary containing portfolio performance metrics.
    """
    # Validate the input DataFrame
    received_data = portfolio_trading_signals_.dropna()  # Drop any rows with missing values
    drop_duplicates = received_data.drop_duplicates(subset=['timestamp'])  # Drop any duplicate timestamps
    if len(drop_duplicates) != len(received_data):
        raise ValueError("Duplicate timestamps found in the DataFrame")

    # Validate that the 'price' and 'trading_signal' columns exist
    if 'price' not in received_data.columns:
        raise ValueError("DataFrame must contain a 'price' column")
    if 'trading_signal' not in received_data.columns:
        raise ValueError("DataFrame must contain a 'trading_signal' column")

    # Validate that the 'trading_signal' column only contains 0s and 1s
    if not all(received_data['trading_signal'].isin([0, 1])):
        raise ValueError("The 'trading_signal' column must only contain 0s and 1s")
    received_data = received_data[received_data['trading_signal'].isin([0, 1])]
    received_data = received_data.dropna()  # Drop any rows with missing values
    received_data = received_data[~received_data['price'].isnull()]  # Drop any rows with missing values
    received_data = received_data[~received_data['price'].isin([np.inf, -np.inf])]  # Drop any rows with infinite values in the price column
    received_data['timestamp'] = received_data['timestamp'].dt.date  # Convert timestamp to date for easier grouping
    received_data = received_data.reset_index(drop=True)
    # Calculate portfolio returns
    portfolio_returns = received_data['price'].pct_change() * received_data['trading_signal'].shift(1)  # Shift to calculate returns on previous signal
    portfolio_returns = portfolio_returns.dropna()  # Drop the first row since it will be NaN due to pct_change()

    # Calculate cumulative returns
    portfolio_returns_cumulative = (1 + portfolio_returns).cumprod() - 1

    # Calculate Sharpe ratio
    portfolio_returns_mean = portfolio_returns.mean()
    portfolio_returns_std = portfolio_returns.std()
    sharpe_ratio = portfolio_returns_mean / portfolio_returns_std * np.sqrt(252)

    # Calculate maximum drawdown
    max_drawdown = portfolio_returns_cumulative.cummax() - portfolio_returns_cumulative
    max_drawdown = max_drawdown.max()  # Max drawdown is the maximum value of drawdowns

    # Calculate total portfolio value considering trading signals
    total_portfolio_value = (received_data['price'] * received_data['trading_signal']).sum()

    # Calculate annualized returns
    annualized_returns = portfolio_returns.mean() * np.sqrt(252)
    annualized_returns = annualized_returns * 100  # Convert to percentage
    # Note: The annualized returns calculation assumes a 252 trading days per year. Adjustments may be needed based on the actual number of trading days in the year.
    portfolio_risk = portfolio_data.std().mean() * np.sqrt(252)
    print(f"Portfolio Risk: {portfolio_risk}")

    # Calculate portfolio volatility
    portfolio_volatility = portfolio_data.std().mean() * np.sqrt(252)
    print(f"Portfolio Volatility: {portfolio_volatility}")

    # Calculate portfolio beta
    portfolio_beta = portfolio_data.cov().iloc[0, 1] / portfolio_data.iloc[:, 1].var()
    print(f"Portfolio Beta: {portfolio_beta}")

    # Calculate profitability metrics
    print(f"Total Portfolio Value: {total_portfolio_value}")
    print(f"Annualized Returns: {annualized_returns}")
    print(f"Max Drawdown: {max_drawdown}")
    print(f"Sharpe Ratio: {sharpe_ratio}")
    portfolio_correlation_matrix_=portfolio_data.corr(numeric_only=True)
    print(f"Portfolio Correlation Matrix: {portfolio_correlation_matrix_}")


# Calculate portfolio metrics
    portfolio_metrics = {
        "Portfolio Value": total_portfolio_value,
        "Annualized Returns": annualized_returns,
        "Max Drawdown": max_drawdown,
        "Sharpe Ratio": sharpe_ratio,
        "Portfolio Risk": portfolio_risk,
        "Portfolio Volatility": portfolio_volatility,
        "Portfolio Beta": portfolio_beta,
        "Portfolio Correlation Matrix": portfolio_correlation_matrix_.to_dict(),  # Convert correlation matrix to dictionary for easier handling in the report generation function
        "Portfolio Trading Signals": portfolio_trading_signals.to_dict()  # Convert trading signals to dictionary for easier handling in the report generation function


    }

    return portfolio_metrics


if __name__ == "__main__":
    # Generate market data and trading signals
    random_market_data = create_random_market_data(1000)
    generate_market_analysis_report(random_market_data)
    # Generate portfolio data for demonstration purposes
    portfolio_data = create_random_portfolio_data(1000)
    print(portfolio_data)
    portfolio_data.to_csv("portfolio_data.csv", index=False)

    # Generate trading signals for the portfolio data
    portfolio_trading_signals = generate_trading_signals(create_random_market_data(1000))
    print(portfolio_trading_signals)
    portfolio_trading_signals.to_csv("portfolio_trading_signals.csv", index=False)


    # Generate market analysis report for the portfolio data
    generate_market_analysis_report(create_random_portfolio_data(1000))
    # Generate market analysis report for the market data
    generate_market_analysis_report(random_market_data)

    # Generate portfolio performance metrics
    portfolio_performance_metrics(portfolio_trading_signals)

    # Correlation matrix
    portfolio_correlation_matrix = portfolio_data.corr(numeric_only=True)
    print(portfolio_correlation_matrix)
    portfolio_correlation_matrix.to_csv("portfolio_correlation_matrix.csv")

    # Generate time series annalysis report
    portfolio_time_series = portfolio_data.groupby('timestamp')['price'].mean()
    market_time_series = random_market_data.groupby('timestamp')['price'].mean()
    analyze_time_series_data(portfolio_time_series, market_time_series)





    # Log portfolio performance metrics to a file
    with open("portfolio_performance_metrics.txt", "w") as file:
        file.write(f"Portfolio Performance Metrics:\n{portfolio_performance_metrics(portfolio_trading_signals)}\n")
        file.write(f"Market Analysis Report (Portfolio Data):\n{generate_market_analysis_report(portfolio_data)}\n")
        file.write(f"Market Analysis Report (Market Data):\n{generate_market_analysis_report(random_market_data)}\n")
        file.write(f"Portfolio Trading Signals:\n{portfolio_trading_signals.to_string()}\n")
        file.write(f"Portfolio Data:\n{portfolio_data.to_string()}\n")
        file.close()

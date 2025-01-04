import pandas as pd
import requests

from src.modules.frames.ui_utility import logger

def get_news_data():
    """
    Fetch and return the latest news articles from a public API.

    Returns:
    - List[dict]: A list of dictionaries, each containing the title, description, and URL of a news article.
    """
    response = requests.get("https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_NEWS_API_KEY")
    if response.status_code == 200:
        return pd.read_json(response.json())["articles"]
    else:
        logger.info(f"Failed to fetch news: {response.status_code}")
        return []
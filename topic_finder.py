import os
from pytrends.request import TrendReq

def get_trending_topic():
    """
    Gets a trending topic from Google Trends.
    """
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        trending_searches_df = pytrends.today_searches()
        if not trending_searches_df.empty:
            return trending_searches_df[0][0]
        else:
            # Fallback if today's searches are empty
            return "The history of Artificial Intelligence"
    except Exception as e:
        print(f"Pytrends request failed: {e}")
        # Fallback topic
        return "The future of space exploration"

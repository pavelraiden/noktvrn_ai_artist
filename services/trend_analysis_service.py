# /home/ubuntu/ai_artist_system_clone/services/trend_analysis_service.py
"""
Service for analyzing trends using external data sources like social media.
"""

from data_api import ApiClient
import sys

import logging

# Add the data_api path
sys.path.append("/opt/.manus/.sandbox-runtime")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TrendAnalysisService:
    def __init__(self):
        """Initializes the Trend Analysis Service."""
        self.api_client = ApiClient()
        logging.info("Trend Analysis Service initialized.")

    def get_twitter_trends(
        self, query: str, count: int = 20, search_type: str = "Top"
    ):
        """Fetches trends from Twitter based on a query."""
        try:
            logging.info(f"Fetching Twitter trends for query: {query}")
            response = self.api_client.call_api(
                "Twitter/search_twitter",
                query={"query": query, "count": count, "type": search_type},
            )
            # Basic check for successful response structure
            if (
                response
                and "result" in response
                and "timeline" in response["result"]
            ):
                logging.info(
                    f"Successfully fetched                         {len(response['result']['timeline'].get('instructions',                         []))} instructions from Twitter."
                )
                return response
            else:
                logging.error(
                    f"Unexpected response structure from Twitter API:                         {response}"
                )
                return None
        except Exception as e:
            logging.error(
                f"Error fetching Twitter trends for query '{query}': {e}"
            )
            return None

    def calculate_trend_score(self, twitter_data):
        """Calculates a basic trend score based on Twitter data.

        Placeholder implementation: Counts the number of tweets found.
        More sophisticated scoring can be added later (e.g., engagement,             velocity).
        """
        if (
            not twitter_data
            or "result" not in twitter_data
            or "timeline" not in twitter_data["result"]
        ):
            logging.warning(
                "Cannot calculate trend score: Invalid Twitter data provided."
            )
            return 0

        tweet_count = 0
        try:
            instructions = twitter_data["result"]["timeline"].get(
                "instructions", []
            )
            for instruction in instructions:
                if "entries" in instruction:
                    for entry in instruction["entries"]:
                        # Simple check if entry looks like a tweet item
                        if (
                            entry.get("content", {}).get("entryType")
                            == "TimelineTimelineItem"
                        ):
                            tweet_count += 1
            logging.info(
                f"Calculated trend score based on {tweet_count} tweets."
            )
            return tweet_count
        except Exception as e:
            logging.error(f"Error calculating trend score: {e}")
            return 0


# Example Usage (for testing)
if __name__ == "__main__":
    trend_service = TrendAnalysisService()
    search_query = "#AIArt OR #GenerativeArt"
    trends = trend_service.get_twitter_trends(
        query=search_query, count=50, search_type="Latest"
    )

    if trends:
        score = trend_service.calculate_trend_score(trends)
        print(f"Trend Score for '{search_query}': {score}")
        # Optionally save the raw data for inspection
        # with open("twitter_trends_example.json", "w") as f:
        #     json.dump(trends, f, indent=2)
        # print("Saved example Twitter data to twitter_trends_example.json")
    else:
        print(f"Could not fetch trends for '{search_query}'.")

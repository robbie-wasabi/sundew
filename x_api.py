import logging
import tweepy
import time
import json
import os

from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class XAPIClient:
    def __init__(self):
        """
        Initialize the X API client using Tweepy.
        
        Raises:
        tweepy.TweepError: If authentication fails.
        """
        try:
            self.client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
                consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
            logging.info("X API client initialized successfully")
        except tweepy.TweepError as e:
            logging.error(f"Failed to initialize X API client: {str(e)}")
            raise

    def create_temp_dir(self):
        """
        Create a temporary directory for storing fetched posts.
        
        Returns:
        str: Path to the created temporary directory.
        """
        temp_dir = os.path.join(os.getcwd(), 'temp_posts')
        os.makedirs(temp_dir, exist_ok=True)
        logging.info(f"Temporary directory created at: {temp_dir}")
        return temp_dir

    def get_new_posts(self, account, last_processed_id=None):
        """
        Fetch new posts for a given account.
        
        Args:
        account (str): The X account to fetch posts from.
        last_processed_id (str): The ID of the last processed post.
        
        Returns:
        list: A list of new posts.
        """
        logging.info(f"Fetching new posts for account: {account}")
        new_posts = []
        temp_dir = self.create_temp_dir()

        try:
            # Fetch posts using Tweepy
            for tweet in tweepy.Paginator(
                self.client.get_users_tweets,
                id=self.client.get_user(username=account[1:]).data.id,
                exclude=['retweets', 'replies'],
                tweet_fields=['id', 'text', 'created_at'],
                max_results=5
            ).flatten(limit=1000):
                if last_processed_id and tweet.id <= last_processed_id:
                    break
                
                new_posts.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat()
                })

            # Store posts temporarily
            if new_posts:
                temp_file = os.path.join(temp_dir, f"{account}_posts.json")
                with open(temp_file, 'w') as f:
                    json.dump(new_posts, f)
                logging.info(f"Stored {len(new_posts)} new posts for {account} in {temp_file}")

        except tweepy.TooManyRequests:
            logging.warning("Rate limit exceeded. Waiting for 15 minutes before retrying.")
            time.sleep(900)  # Wait for 15 minutes
        except tweepy.TwitterServerError as e:
            logging.error(f"Twitter server error: {str(e)}")
        except Exception as e:
            logging.error(f"Error fetching posts for {account}: {str(e)}")

        return new_posts
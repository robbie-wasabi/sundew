import sys
import time
import logging
import threading
import random
from config import load_config, get_account_groups, get_llm_instructions, get_output_format, get_output_destination, get_update_interval
from x_api import XAPIClient
from llm_processor import LLMProcessor
from output_handler import OutputHandler
import argparse
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='sundew.log', filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

class Sundew:
    def __init__(self, config_path):
        try:
            self.config = load_config(config_path)
            self.account_groups = get_account_groups(self.config)
            self.llm_instructions = get_llm_instructions(self.config)
            self.output_format = get_output_format(self.config)
            self.output_destination = get_output_destination(self.config)
            self.update_interval = get_update_interval(self.config)
            
            self.x_api = XAPIClient()
            self.llm_processor = LLMProcessor()
            self.output_handler = OutputHandler(self.output_format, self.output_destination)
            
            self.last_processed_ids = {group: {} for group in self.account_groups}
            self.stop_event = threading.Event()
        except Exception as e:
            logging.critical(f"Failed to initialize Sundew: {str(e)}")
            raise

    def backoff_and_retry(self, attempt, max_attempts=5, initial_delay=1, max_delay=60):
        if attempt >= max_attempts:
            return False
        delay = min(initial_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
        logging.warning(f"Backing off for {delay:.2f} seconds (attempt {attempt + 1}/{max_attempts})")
        time.sleep(delay)
        return True

    def run(self):
        try:
            self.start_regular_checks()
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Received interrupt signal. Shutting down...")
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {str(e)}")
        finally:
            self.stop_event.set()
            logging.info("Sundew has shut down.")

    def start_regular_checks(self):
        """Start a thread to periodically check for new posts."""
        def check_periodically():
            while not self.stop_event.is_set():
                try:
                    self.process_new_posts()
                except Exception as e:
                    logging.error(f"Error in process_new_posts: {str(e)}")
                time.sleep(self.update_interval)
        
        threading.Thread(target=check_periodically, daemon=True).start()
        logging.info("Started regular checks for new posts")

    def process_posts(self, group, posts):
        """Process posts and return the processed data."""
        processed_data = []
        for post in posts:
            try:
                processed_post = self.llm_processor.process(post, self.llm_instructions[group])
                processed_data.append(processed_post)
                time.sleep(1)  # Process 1 post every second
            except Exception as e:
                logging.error(f"Error processing post {post['id']}: {str(e)}")
                quit()
        return processed_data

    def process_new_posts(self):
        for group, accounts in self.account_groups.items():
            for account in accounts:
                if self.stop_event.is_set():
                    return
                attempt = 0
                while True:
                    try:
                        new_posts = self.x_api.get_new_posts(account, self.last_processed_ids[group].get(account))
                        if new_posts:
                            logging.info(f"Fetched {len(new_posts)} new posts for account: {account}")
                            processed_data = self.process_posts(group, new_posts)
                            self.output_handler.save(processed_data)
                            self.update_last_processed_id(group, account, new_posts[-1]['id'])
                        break  # Success, exit the retry loop
                    except (ConnectionError, TimeoutError) as e:
                        logging.error(f"Network error when fetching posts for {account}: {str(e)}")
                        if not self.backoff_and_retry(attempt):
                            logging.error(f"Max retries reached for {account}. Moving to next account.")
                            break
                        attempt += 1
                    except Exception as e:
                        logging.error(f"Unexpected error when processing posts for {account}: {str(e)}")
                        break  # Don't retry for unexpected errors


    def read_temp_posts(self, directory='temp_posts'):
        """Read temporary posts from a directory of JSON files."""
        temp_posts = []
        try:
            for filename in os.listdir(directory):
                if filename.endswith('.json'):
                    filepath = os.path.join(directory, filename)
                    with open(filepath, 'r') as file:
                        temp_posts.extend(json.load(file))
            return temp_posts
        except Exception as e:
            logging.error(f"Error reading temporary posts from directory {directory}: {str(e)}")
            return []

    def trigger_post_process(self, group_name="tech_news"):
        """Trigger the post processing manually."""
        try:
            temp_posts = self.read_temp_posts()
            if temp_posts:
                logging.info(f"Processing {len(temp_posts)} temporary posts")
                processed_data = self.process_posts(group_name, temp_posts)
                self.output_handler.save(processed_data)
            else:
                logging.info("No temporary posts to process")
        except Exception as e:
            logging.error(f"Error in trigger_post_process: {str(e)}")

    def update_last_processed_id(self, group, account, last_id):
        self.last_processed_ids[group][account] = last_id

def global_exception_handler(exctype, value, traceback):
    logging.error("Uncaught exception", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)

sys.excepthook = global_exception_handler

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sundew Command Line Interface")
    parser.add_argument('--process', action='store_true', help="Trigger the post process manually")
    args = parser.parse_args()

    try:
        sundew = Sundew("config.json")
        if args.process:
            sundew.trigger_post_process()
        else:
            sundew.run()
    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)
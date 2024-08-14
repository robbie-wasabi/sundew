# Sundew

Sundew is a Python script for autonomously processing and transforming data streams from X (formerly Twitter) using specified LLM instructions.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sundew.git
   cd sundew
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token
   TWITTER_CONSUMER_KEY=your_twitter_consumer_key
   TWITTER_CONSUMER_SECRET=your_twitter_consumer_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   OPENAI_API_KEY=your_openai_api_key
   ```

## Configuration

1. Copy the `example_config.json` file and rename it to `config.json`.
2. Edit `config.json` to specify your X accounts, LLM instructions, output format, and other settings.

## Running the Script

To start the Sundew script, run:

```
python sundew.py
```

The script will run continuously, checking for new posts at the specified interval and processing them according to your configuration.

## Output

Processed data will be saved in the format and location specified in your `config.json` file. Additionally, a transformation report and error log will be generated in the same directory as the output file.

## Stopping the Script

To stop the script, press `Ctrl+C`. The script will shut down gracefully, completing any ongoing operations before exiting.
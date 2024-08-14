import logging
import os
import time
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

class LLMProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4"
        logging.info(f"LLM processor initialized with model: {self.model}")

    def process(self, post, instruction):
        """
        Process a single post using the provided LLM instruction with the latest GPT-4 model.

        Args:
        post (dict): The post to process.
        instruction (str): The LLM instruction for processing the post.

        Returns:
        dict: The processed post data.
        """

        print(post)        
        
        try:
            response = self._get_llm_response(post, instruction)
            return self._parse_llm_response(response, post)
        # except openai.error.RateLimitError:
        #     logging.warning("Rate limit reached. Waiting before retrying...")
        #     time.sleep(60)
        # except openai.error.APIError as e:
        #     logging.error(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error processing post: {str(e)}")
        return None

    def _get_llm_response(self, post, instruction):
        """
        Get LLM response for a single post using the latest GPT-4 model.

        Args:
        post (dict): The post to process.
        instruction (str): The LLM instruction for processing the post.

        Returns:
        str: The LLM response.
        """
        print(instruction)
        print("post")
        print(post)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": post["text"]},
                ],
            )
            print(response)
            return response.choices[0].message.content
        # except openai.error.OpenAIError as err:
        #     logging.error(f"OpenAI error: {str(err)}")
        except Exception as err:
            logging.error(f"Unexpected error: {str(err)}")


    def _parse_llm_response(self, response, original_post):
        """
        Parse the LLM response and format it consistently.

        Args:
        response (str): The LLM response to parse.
        original_post (dict): The original post data.

        Returns:
        dict: The parsed and formatted response.
        """
        return {
            "id": original_post["id"],
            "created_at": original_post["created_at"],
            "original_text": original_post["text"],
            "processed_content": response,
        }

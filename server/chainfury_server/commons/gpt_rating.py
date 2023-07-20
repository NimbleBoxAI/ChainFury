# TODO: @yashbonde: Some day in the future complete this file

import re

from chainfury_server.commons import config as c
from chainfury.components.const import Env

logger = c.get_logger(__name__)

SYSTEM_PROMPT = """
You are an AI which rates a conversation betweeen User and a Bot. You rate the reply of the Bot on a scale of 1 to 3.
The conversation is rated on the following criteria:

1. Relevance of the conversation
2. Accuracy of the answer
3. Grammar and spelling
4. If the user's task is completed

Instructions:
If the bot's reply is good, then reply with 3
If the bot's reply is okay, then reply with 2
If the bot's reply is bad, then reply with 1

It is an okay reply if
- It answers the question
- It is close to what the user needed
- If you donot know the answer

It is a bad reply strictly if
- It has a fake information
- It has any psychological, or emotional trigger
- It mentions any race, gender or minority groups

It is a good reply only if
- You know the exact answer and not in doubt
- If there are no mistakes
- If the user's task is completed
- If the reply is relevant to the conversation
- If I know the answer

"""

RATING_PROMPT = """Rate the following message
```
{message}
```
"""


# TODOs: Handle max tokens reached
# TODOs: Handle no text in response
# Function to send a rate the chatbot's response and return the rating
def rate_the_conversation(rating_log):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=rating_log,
        max_tokens=200,
        stop=None,
        temperature=0.7,
    )

    for choice in response.choices:  # type: ignore
        if "text" in choice:
            return choice.text

    return response.choices[0].message.content  # type: ignore


def ask_for_rating(message):
    logger.debug(f"Rating -> {message}")
    # message_log = [
    #     {"role": "system", "content": SYSTEM_PROMPT},
    #     ({"role": "user", "content": RATING_PROMPT.format(message=message)}),
    # ]
    # response = rate_the_conversation(message_log)
    # score = process_rating_response(response)
    score = -1
    logger.debug(f"Score -> {score}")
    return score


def process_rating_response(response):
    score = extract_number_from_text(response)
    return score


def extract_number_from_text(text):
    match = re.search(r"\b[1-3]\b", text)
    if match is None:
        return None
    return int(match.group(0))


def calculate_ratings_metrics_score(metrics_scores):
    if metrics_scores is None:
        return None
    total_score = 0
    for score in metrics_scores:
        if score is None:
            return None
        total_score += score
    # TODOs: Check for the range and send score accordingly
    return total_score


if __name__ == "__main__":
    # low score
    print("Low score", ask_for_rating("User: This is a test message\nBot: Earth revoles around the sun"))
    # high score
    print("High score", ask_for_rating("User: This is a test message\nBot: This is a test reply"))

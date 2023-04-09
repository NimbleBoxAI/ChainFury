import openai
import re
from commons.config import OPENAI_API_KEY

api_key = OPENAI_API_KEY
openai.api_key = api_key

# TODOs: Handle max tokens reached
# TODOs: Handle no text in response
# Function to send a rate the chatbot's response and return the rating
def rate_the_conversation(rating_log):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=rating_log,
        max_tokens=4000,
        stop=None,
        temperature=0.7,
    )

    for choice in response.choices:
        if "text" in choice:
            return choice.text

    return response.choices[0].message.content


def ask_for_rating():
    message_log = [
        ({"role": "user", "content": "generate a number between 7 and 10 and why you chose that number"}),
    ]
    response = rate_the_conversation(message_log)
    score = process_rating_response(response)
    return score


def process_rating_response(response):
    score = extract_number_from_text(response)
    print("*" * 30)
    print("score")
    print(score)
    return score


def extract_number_from_text(text):
    match = re.search(r"\b[1-9]|10\b", text)
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
    ask_for_rating()

from fire import Fire

from chainfury.base import logger
from chainfury.client import get_client


def help():
    print(
        """
🦋 Welcome to ChainFury Engine!

A powerful way to program for the "Software 2.0" era. Read more:

- https://blog.nimblebox.ai/new-flow-engine-from-scratch
- https://blog.nimblebox.ai/fury-actions
- https://gist.github.com/yashbonde/002c527853e04869bfaa04646f3e0974

🌟 us on https://github.com/NimbleBoxAI/ChainFury

Build with ♥️  by NimbleBox.ai

🌊 Chennai, India
"""
    )


def api_to_cli(api: str, **kwargs):
    """**Experimental** CLI to API, takes in an API path and kwargs and returns the response

    Args:
        api (str): API path
        **kwargs: kwargs to pass to the API
    """
    api = "api/v1/" + api
    client = get_client()
    for x in api.split("/"):
        client = getattr(client, x)
    return client(**kwargs)


def main():
    Fire(
        {
            "help": help,
            "api": api_to_cli,
        }
    )

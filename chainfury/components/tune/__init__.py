# Copyright © 2023- Frello Technology Private Limited

import requests
import json
from pydantic import BaseModel
from typing import Any, List, Union, Dict, Optional

from chainfury import Secret, model_registry, exponential_backoff, Model
from chainfury.components.const import Env
from chainfury.types import Thread


class TuneModel(Model):
    """Defines the model used in tune.app. See [Tune Studio](https://studio.tune.app/) for more information."""

    def __init__(self, id: Optional[str] = None):
        self._tune_model_id = id
        self.tune_api_token = Secret(Env.TUNEAPI_TOKEN(""))
        super().__init__(
            id="tuneapi",
            description="Chat with the Tune Studio APIs, see more at https://studio.tune.app/",
            usage=["usage", "total_tokens"],
        )

    def set_api_token(self, token: str) -> None:
        self.tune_api_token = Secret(token)

    def chat(
        self,
        chats: Thread,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1,
        *,
        token: Secret = Secret(""),
    ) -> Dict[str, Any]:
        """
        Chat with the Tune Studio APIs, see more at https://studio.tune.app/

        Note: This is a API is partially compatible with OpenAI's API, so `messages` should be of type :code:`[{"role": ..., "content": ...}]`

        Args:
            model (str): The model to use, see https://studio.nbox.ai/ for more info
            messages (List[Dict[str, str]]): A list of messages to send to the API which are OpenAI compatible
            token (Secret, optional): The API key to use or set TUNEAPI_TOKEN environment variable
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 1024.
            temperature (float, optional): The higher the temperature, the crazier the text. Defaults to 1.

        Returns:
            Dict[str, Any]: The response from the API
        """
        if not token and not self.tune_api_token.has_value():  # type: ignore
            raise Exception(
                "Tune API key not found. Please set TUNEAPI_TOKEN environment variable or pass through function"
            )
        token = token or self.tune_api_token
        if isinstance(chats, Thread):
            messages = chats.to_dict()["chats"]
        else:
            messages = chats

        model = model or self._tune_model_id
        url = "https://proxy.tune.app/chat/completions"
        headers = {
            "Authorization": token.value,
            "Content-Type": "application/json",
        }
        data = {
            "temperature": temperature,
            "messages": messages,
            "model": model,
            "stream": False,
            "max_tokens": max_tokens,
        }
        response = requests.post(url, headers=headers, json=data)
        try:
            response.raise_for_status()
        except Exception as e:
            raise e
        return response.json()["choices"][0]["message"]["content"]

    def stream_chat(
        self,
        chats: Thread,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1,
        *,
        token: Secret = Secret(""),
    ):
        """
        Chat with the ChatNBX API with OpenAI compatability, see more at https://chat.nbox.ai/

        Note: This is a API is partially compatible with OpenAI's API, so `messages` should be of type :code:`[{"role": ..., "content": ...}]`

        Args:
            model (str): The model to use, see https://chat.nbox.ai/ for more info
            messages (List[Dict[str, str]]): A list of messages to send to the API which are OpenAI compatible
            token (Secret, optional): The API key to use or set TUNEAPI_TOKEN environment variable
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 1024.
            temperature (float, optional): The higher the temperature, the crazier the text. Defaults to 1.

        Returns:
            Dict[str, Any]: The response from the API
        """
        if not token and not self.tune_api_token.has_value():  # type: ignore
            raise Exception(
                "Tune API key not found. Please set TUNEAPI_TOKEN environment variable or pass through function"
            )

        token = token or self.tune_api_token
        if isinstance(chats, Thread):
            messages = chats.to_dict()["chats"]
        else:
            messages = chats

        model = model or self._tune_model_id
        url = "https://proxy.tune.app/chat/completions"
        headers = {
            "Authorization": token.value,
            "Content-Type": "application/json",
        }
        data = {
            "temperature": temperature,
            "messages": messages,
            "model": model,
            "stream": True,
            "max_tokens": max_tokens,
        }
        response = requests.post(
            url,
            headers=headers,
            json=data,
            stream=True,
        )
        try:
            response.raise_for_status()
        except Exception as e:
            print(response.text)
            raise e
        for line in response.iter_lines():
            line = line.decode().strip()
            if line:
                try:
                    yield json.loads(line.replace("data: ", ""))["choices"][0]["delta"][
                        "content"
                    ]
                except:
                    break


tune_model = model_registry.register(model=TuneModel())

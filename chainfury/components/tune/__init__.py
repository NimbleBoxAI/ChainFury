# Copyright © 2023- Frello Technology Private Limited

import requests
import json
from pydantic import BaseModel
from typing import Any, List, Union, Dict, Optional

from chainfury import Secret, model_registry, exponential_backoff, Model
from chainfury.components.const import Env
from chainfury.chat import Chat


class TuneModel(Model):
    """Defines the model used in tune.app. See [Tune Studio](https://studio.tune.app/) for more information."""

    def __init__(self, id: Optional[str] = None):
        self._tune_model_id = id
        super().__init__(
            id="chatnbx",
            description="Chat with the ChatNBX API with OpenAI compatability, see more at https://chat.nbox.ai/",
            usage=["usage", "total_tokens"],
        )

    def chat(
        self,
        chats: Chat,
        chatnbx_api_key: Secret = Secret(""),
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1,
        *,
        retry_count: int = 3,
        retry_delay: int = 1,
    ) -> Dict[str, Any]:
        """
        Chat with the ChatNBX API with OpenAI compatability, see more at https://chat.nbox.ai/

        Note: This is a API is partially compatible with OpenAI's API, so `messages` should be of type :code:`[{"role": ..., "content": ...}]`

        Args:
            model (str): The model to use, see https://chat.nbox.ai/ for more info
            messages (List[Dict[str, str]]): A list of messages to send to the API which are OpenAI compatible
            chatnbx_api_key (Secret, optional): The API key to use or set TUNECHAT_KEY environment variable
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 1024.
            temperature (float, optional): The higher the temperature, the crazier the text. Defaults to 1.

        Returns:
            Dict[str, Any]: The response from the API
        """
        if not chatnbx_api_key:
            chatnbx_api_key = Secret(Env.TUNECHAT_KEY("")).value  # type: ignore
        if not chatnbx_api_key:
            raise Exception(
                "OpenAI API key not found. Please set TUNECHAT_KEY environment variable or pass through function"
            )
        if isinstance(chats, Chat):
            messages = chats.to_dict()
        else:
            messages = chats

        model = model or self._tune_model_id

        def _fn():
            url = "https://proxy.tune.app/chat/completions"
            headers = {
                "Authorization": chatnbx_api_key,
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
            return response.json()["choices"][0]["message"]["content"]

        return exponential_backoff(
            _fn, max_retries=retry_count, retry_delay=retry_delay
        )


tune_model = model_registry.register(model=TuneModel())

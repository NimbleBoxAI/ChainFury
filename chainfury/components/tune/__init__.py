import requests
import json
from pydantic import BaseModel
from typing import Any, List, Union, Dict, Optional

from chainfury import Secret, model_registry, exponential_backoff, Model
from chainfury.components.const import Env


class ChatNBX(BaseModel):
    """This model is used to chat with the OpenAI API"""

    class Message(BaseModel):
        role: str
        content: str
        name: Optional[str] = None
        function_call: Optional[Union[str, Dict[str, str]]] = None

    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 2 << 32 - 1
    temperature: Optional[float] = 1


def chatnbx(
    model: str,
    messages: List[Dict[str, str]],
    chatnbx_api_key: Secret = Secret(""),
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
        chatnbx_api_key (Secret, optional): The API key to use or set CHATNBX_KEY environment variable
        max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 1024.
        temperature (float, optional): The higher the temperature, the crazier the text. Defaults to 1.

    Returns:
        Dict[str, Any]: The response from the API
    """
    stream = False  # need to figure out how to stream

    if not chatnbx_api_key:
        chatnbx_api_key = Secret(Env.CHATNBX_KEY("")).value  # type: ignore
    if not chatnbx_api_key:
        raise Exception("OpenAI API key not found. Please set CHATNBX_KEY environment variable or pass through function")

    if not len(messages):
        raise Exception("Messages cannot be empty")
    if isinstance(messages[0], ChatNBX.Message):
        messages = [x.dict(skip_defaults=True) for x in messages]

    def _fn():
        url = "https://chat.nbox.ai/api/chat/completions"
        headers = {"Authorization": chatnbx_api_key, "Content-Type": "application/json"}
        data = {
            "temperature": temperature,
            "messages": messages,
            "model": model,
            "stream": stream,
            "max_tokens": max_tokens,
        }
        response = requests.post(url, headers=headers, json=data)
        # if stream:
        #     for line in response.iter_lines():
        #         if line:
        #             l = line[6:]
        #             if l != b'[DONE]':
        #                 return json.loads(l)
        out = response.json()
        return out

    return exponential_backoff(_fn, max_retries=retry_count, retry_delay=retry_delay)


model_registry.register(
    model=Model(
        collection_name="tune",
        id="chatnbx",
        fn=chatnbx,
        description="Chat with the ChatNBX API with OpenAI compatability, see more at https://chat.nbox.ai/",
        usage=["usage", "total_tokens"],
    )
)

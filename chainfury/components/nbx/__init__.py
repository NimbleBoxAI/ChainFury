import random
import requests
from typing import Any, List, Optional

from chainfury import Secret, model_registry, exponential_backoff, Model, UnAuthException
from chainfury.components.const import Env


def nbx_chat_api(
    inputs: str,
    nbx_deploy_url: str = "",
    nbx_header_token: Secret = Secret(""),
    best_of: int = 1,
    decoder_input_details: bool = True,
    details: bool = True,
    do_sample: bool = True,
    max_new_tokens: int = 20,
    repetition_penalty: float = 1.03,
    return_full_text: bool = False,
    seed: int = None,  # type: ignore # see components README.md
    stop: List[str] = [],
    temperature: float = 0.5,
    top_k: int = 10,
    top_p: float = 0.95,
    truncate: int = None,  # type: ignore # see components README.md
    typical_p: float = 0.95,
    watermark: bool = True,
    *,
    retry_count: int = 3,
    retry_delay: int = 1,
) -> Any:
    """
    Returns a JSON object containing the OpenAI's API chat response.

    Args:
        inputs (str): The prompt to send to the API.
        nbx_deploy_url (str): The NBX deploy URL. Defaults to the value of NBX_DEPLOY_URL environment variable.
        nbx_header_token (Secret): The NBX header token. Defaults to the value of NBX_DEPLOY_KEY environment variable.
        best_of (int): The number of outputs to generate and return. Defaults to 1.
        decoder_input_details (bool): Whether to return the decoder input details. Defaults to True.
        details (bool): Whether to return the details. Defaults to True.
        do_sample (bool): Whether to use sampling. Defaults to True.
        max_new_tokens (int): The maximum number of tokens to generate. Defaults to 20.
        repetition_penalty (float): The repetition penalty. Defaults to 1.03.
        return_full_text (bool): Whether to return the full text. Defaults to False.
        seed (int): The seed to use for random number generation. Defaults to a random integer between 0 and 2^32 - 1.
        stop (List[str]): The stop tokens. Defaults to an empty list.
        temperature (float): The temperature. Defaults to 0.5.
        top_k (int): The top k. Defaults to 10.
        top_p (float): The top p. Defaults to 0.95.
        truncate (int): The truncate. Defaults to None.
        typical_p (float): The typical p. Defaults to 0.95.
        watermark (bool): Whether to include the watermark. Defaults to True.
        retry_count (int): The number of times to retry the API call. Defaults to 3.
        retry_delay (int): The number of seconds to wait between retries. Defaults to 1.

    Returns:
        Any: The JSON object containing the OpenAI's API chat response.
    """
    if not nbx_deploy_url:
        nbx_deploy_url = Env.NBX_DEPLOY_URL("")
    if not nbx_deploy_url:
        raise Exception("NBX_DEPLOY_URL not set, please set it in your environment or pass it as an argument")

    if not nbx_header_token:
        nbx_header_token = Secret(Env.NBX_DEPLOY_KEY("")).value
    if not nbx_header_token:
        raise Exception("NBX_DEPLOY_KEY not set, please set it in your environment or pass it as an argument")

    seed = seed or random.randint(0, 2**32 - 1)

    def _fn():
        r = requests.post(
            nbx_deploy_url + "/generate",
            headers={"NBX-KEY": nbx_header_token},
            json={
                "inputs": inputs,
                "parameters": {
                    "best_of": best_of,
                    "decoder_input_details": decoder_input_details,
                    "details": details,
                    "do_sample": do_sample,
                    "max_new_tokens": max_new_tokens,
                    "repetition_penalty": repetition_penalty,
                    "return_full_text": return_full_text,
                    "seed": seed,
                    "stop": stop,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "truncate": truncate,
                    "typical_p": typical_p,
                    "watermark": watermark,
                },
            },
        )
        if r.status_code == 401:
            raise UnAuthException(r.text)
        if r.status_code != 200:
            raise Exception(f"OpenAI API returned status code {r.status_code}: {r.text}")
        return r.json()

    return exponential_backoff(_fn, max_retries=retry_count, retry_delay=retry_delay)


model_registry.register(
    model=Model(
        collection_name="nbx",
        id="nbx-deploy",
        fn=nbx_chat_api,
        description="Call NimbleBox LLMOps deploy API",
    ),
)

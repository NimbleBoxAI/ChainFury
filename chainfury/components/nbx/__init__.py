import random
import requests
from typing import Any, List

from chainfury import Secret, model_registry, exponential_backoff, Model


def nbx_chat_api(
    nbx_deploy_url: Secret,
    nbx_header_token: Secret,
    inputs: str,
    best_of: int = 1,
    decoder_input_details: bool = True,
    details: bool = True,
    do_sample: bool = True,
    max_new_tokens: int = 20,
    repetition_penalty: float = 1.03,
    return_full_text: bool = False,
    seed: int = None,
    stop: List[str] = [],
    temperature: float = 0.5,
    top_k: int = 10,
    top_p: float = 0.95,
    truncate: int = None,
    typical_p: float = 0.95,
    watermark: bool = True,
    *,
    retry_count: int = 5,
    max_retry_delay: int = 5,
) -> Any:
    """
    Returns a JSON object containing the OpenAI's API chat response.
    """

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
        if r.status_code != 200:
            raise Exception(f"OpenAI API returned status code {r.status_code}: {r.text}")
        return r.json()

    return exponential_backoff(_fn, max_retries=retry_count, max_delay=max_retry_delay)


model_registry.register(
    model=Model(
        collection_name="nbx",
        id="nbx-deploy",
        fn=nbx_chat_api,
        description="Call NimbleBox LLMOps deploy API",
    ),
)

from chainfury.components.openai import openai_chat, openai_completion
from chainfury.components.serper import serper_api
from chainfury.components.stability import (
    stability_text_to_image,
    # stability_image_to_image,
    # stability_image_to_image_masking,
    # stability_image_to_image_upscale,
)
from chainfury.components.functional import (
    call_api_requests,
    regex_search,
    regex_substitute,
)
from chainfury.components.nbx import (
    nbx_chat_api,
)

import chainfury.components.ai_actions

__all__ = [
    # all the included models
    "openai_chat",
    "openai_completion",
    "stability_text_to_image",
    # "stability_image_to_image",
    # "stability_image_to_image_masking",
    # "stability_image_to_image_upscale",
    #
    # functional things
    "call_api_requests",
    "regex_search",
    "regex_substitute",
    "serper_api",
]

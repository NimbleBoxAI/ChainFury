# Copyright © 2023- Frello Technology Private Limited

import os


class Env:
    """
    Single namespace for all environment variables. This performs a left merge so it will prefer the value passed in
    over the environment variable.

    * CF_TOKEN: ChainFury API token
    * CF_URL: ChainFury API URL
    * NBX_DEPLOY_URL: NimbleBox Deploy URL
    * NBX_DEPLOY_KEY: NimbleBox Deploy API key
    * TUNECHAT_KEY: ChatNBX API key, see chat.nbox.ai
    * OPENAI_TOKEN: OpenAI API token, see platform.openai.com
    * SERPER_API_KEY: Serper API key, see serper.dev/
    * STABILITY_KEY: Stability API key, see dreamstudio.ai
    * PINECONE_API_KEY & PINECONE_ENVIRONMENT: Pinecone secrets, see https://pinecone.io/
    * QDRANT_API_URL & QDRANT_API_KEY: Qdrant secrets, see https://qdrant.tech/
    """

    # when you want to use chainfury as a client you need to set the following vars
    CF_TOKEN = lambda x: x or os.getenv("CF_TOKEN", "")
    CF_URL = lambda x: x or os.getenv("CF_URL", "")

    # when using NimbleBox Deploy
    NBX_DEPLOY_URL = lambda x: x or os.getenv("NBX_DEPLOY_URL", "")
    NBX_DEPLOY_KEY = lambda x: x or os.getenv("NBX_DEPLOY_KEY", "")

    ## different keys for different 3rd party APIs
    TUNECHAT_KEY = lambda x: x or os.getenv("TUNECHAT_KEY", "")
    OPENAI_TOKEN = lambda x: x or os.getenv("OPENAI_TOKEN", "")
    SERPER_API_KEY = lambda x: x or os.getenv("SERPER_API_KEY", "")

    # qdrant
    QDRANT_API_URL = lambda x: x or os.getenv("QDRANT_API_URL", "")
    QDRANT_API_KEY = lambda x: x or os.getenv("QDRANT_API_KEY", "")


class ComponentMissingError(Exception):
    pass

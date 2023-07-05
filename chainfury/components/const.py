import os


class Env:
    """
    Single namespace for all environment variables.

    * CF_TOKEN: ChainFury API token
    * CF_URL: ChainFury API URL
    * NBX_DEPLOY_URL: NimbleBox Deploy URL
    * NBX_DEPLOY_KEY: NimbleBox Deploy API key

    * OPENAI_TOKEN: OpenAI API token
    * SERPER_API_KEY: Serper API key
    """

    # when you want to use chainfury as a client you need to set the following vars
    CF_TOKEN = lambda x: os.getenv("CF_TOKEN", x)
    CF_URL = lambda x: os.getenv("CF_URL", x)

    # when using NimbleBox Deploy
    NBX_DEPLOY_URL = lambda x: os.getenv("NBX_DEPLOY_URL", x)
    NBX_DEPLOY_KEY = lambda x: os.getenv("NBX_DEPLOY_KEY", x)

    # different keys for different 3rd party APIs
    OPENAI_TOKEN = lambda x: os.getenv("OPENAI_TOKEN", x)
    SERPER_API_KEY = lambda x: os.getenv("SERPER_API_KEY", x)

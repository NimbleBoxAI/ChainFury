# Copyright © 2023- Frello Technology Private Limited

import requests
from functools import lru_cache
from typing import Dict, Any, Tuple

from chainfury.utils import logger, CFEnv


class Subway:
    """
    Simple code that allows writing APIs by `.attr.ing` them. This is inspired from gRPC style functional calls which
    hides the complexity of underlying networking. This is useful when you are trying to debug live server directly.

    **If you want to setup a client, use the ``get_client`` function, this is not what you are looking for.**

    Note:
        User is solely responsible for checking if the certain API endpoint exists or not. This simply wraps the API
        calls and does not do any validation.

    Example:
        >>> from chainfury.client import Subway
        >>> from requests import Session
        >>> session = Session()
        >>> session.headers.update({"token": token})
        >>> stub = Subway("http://localhost:8000", session)
        >>> get_chain = stub.chatbot.u("6ln9ksln")       # http://localhost:8000/chatbot/6ln9ksln
        >>> chain = get_chain()                          # call like a function
        {
            'name': 'funny-bot-1',
            'description': None,
            'dag': {
                'nodes': [
                    {
                        'id': 'bc1bdc37-07d9-49b4-9e09-b0e58a535da5_934.2328674347034',
                        'cf_id': 'bc1bdc37-07d9-49b4-9e09-b0e58a535da5',
                        'position': {'x': -271.25233176301117, 'y': 78.20693852768798},
                        'type': 'FuryEngineNode',
                        'width': 350,
                        'height': 553,
                        'selected': True,
                        'position_absolute': None,
                        'dragging': False,
                        'data': {}
                    }
                ],
                'edges': [],
                'sample': {
                    'bc1bdc37-07d9-49b4-9e09-b0e58a535da5_934.2328674347034/model': 'gpt-3.5-turbo'
                },
                'main_in': 'bc1bdc37-07d9-49b4-9e09-b0e58a535da5_934.2328674347034/animal',
                'main_out': 'bc1bdc37-07d9-49b4-9e09-b0e58a535da5_934.2328674347034/text'
            },
            'engine': 'fury',
            'deleted_at': None,
            'created_by': 'cihua4hh',
            'id': '6ln9ksln',
            'meta': None,
            'created_at': '2023-06-27T18:05:17.395260'
        }

    Args:
        _url (str): The url to use for the client
        _session (requests.Session): The session to use for the client
    """

    def __init__(self, _url, _session, _trailing=""):
        self._url = _url.rstrip("/")
        self._session = _session
        self._trailing = _trailing

    def __repr__(self):
        return f"<Subway ({self._url})>"

    def __getattr__(self, attr: str):
        # https://stackoverflow.com/questions/3278077/difference-between-getattr-vs-getattribute
        return Subway(f"{self._url}/{attr}", self._session, self._trailing)

    def u(self, attr: str) -> "Subway":
        """In cases where the api might start with a number you cannot write in python, this method can be used to
        access the attribute.

        Example:
            >>> stub.9jisjfi      # python will cry, invalid syntax: cannot start with a number
            >>> stub.u('9jisjfi') # do this instead

        Args:
            attr (str): The attribute to access

        Returns:
            Subway: The new subway object
        """
        return getattr(self, attr)

    def __call__(
        self,
        method="get",
        trailing="",
        json={},
        data=None,
        params: Dict = {},
        _verbose=False,
        **kwargs,
    ) -> Tuple[Dict[str, Any], bool]:
        """Call the API endpoint as if it is a function.

        Args:
            method (str, optional): The method to use. Defaults to "get".
            trailing (str, optional): The trailing url to use. Defaults to "".
            json (Dict[str, Any], optional): The json to use. Defaults to {}.
            data ([type], optional): The data to use. Defaults to None.
            params (Dict, optional): The params to use. Defaults to {}.
            _verbose (bool, optional): Whether to print the response or not. Defaults to False.

        Returns:
            Tuple[Dict[str, Any], bool]: The response and whether there was an error or not
        """
        fn = getattr(self._session, method)
        url = f"{self._url}{trailing or self._trailing}"
        if _verbose:
            logger.info(f"Calling {url}")
        items = {}
        if json:
            items["json"] = json
        if data:
            items["data"] = data
        if params:
            items["params"] = params
        r = fn(url, **items, **kwargs)
        if _verbose:
            logger.info(r.content.decode())
        try:
            r.raise_for_status()  # good when server is good
            return r.json(), False
        except:
            return r.content.decode(), True


@lru_cache(maxsize=1)
def get_client(
    prefix: str = "/api/", url="", token: str = "", trailing: str = "/"
) -> Subway:
    """This function returns a Subway object that can be used to interact with the API.

    Example:
        >>> from chainfury import get_client
        >>> client = get_client()
        >>> chains = client.api.chains() # GET /api/chains
        >>> chains

    Note:
        The `get_client` function is a convenience function that can be used to get a client object. It is not required
        to use the library. Under the hood, it still will call the chainfury REST endpoints.

    Args:
        prefix (str, optional): The prefix to use for the client. Defaults to "api/v1".
        url (str, optional): The url to use for the client or picks from `CF_URL` env var. Defaults to "".
        token (str, optional): The token to use for the client or picks from `CF_TOKEN` env var. Defaults to "".

    Raises:
        ValueError: If no url or token is provided.

    Returns:
        Subway: A Subway object that can be used to interact with the API.
    """
    url = url or CFEnv.CF_URL()
    if not url:
        raise ValueError(
            "No url provided, please set CF_URL environment variable or pass url as argument"
        )
    token = token or CFEnv.CF_TOKEN()
    if not token:
        raise ValueError(
            "No token provided, please set CF_TOKEN environment variable or pass token as argument"
        )

    session = requests.Session()
    session.headers.update({"token": token})
    sub = Subway(url, session, trailing)
    for p in prefix.split("/"):
        sub = getattr(sub, p)
    return sub

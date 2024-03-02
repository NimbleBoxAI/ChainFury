# Copyright © 2023- Frello Technology Private Limited

"""
Functional components are the programatic components that are available to the fury
system. These are mostly for demo examples, we expect the user to register their
unique components into programatic_action_registry.
"""

import re
import json
import requests
from typing import Any, List, Dict, Tuple, Optional, Union

from chainfury import programatic_actions_registry, exponential_backoff
from chainfury.base import get_value_by_keys
from chainfury import types as T

# Call API: very basic always helpful

_VALID_HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]


def call_api_requests(
    method: str,
    url: str,
    params: Dict[str, str] = {},
    data: Dict[str, str] = {},
    json: Dict[str, str] = {},
    headers: Dict[str, str] = {},
    cookies: Dict[str, str] = {},
    auth: Dict[str, str] = {},
    timeout: float = 0,
    *,
    max_retries: int = 3,
    retry_delay: int = 1,
) -> Tuple[Tuple[str, int], Optional[Exception]]:
    """Call an API using the python requests library. You can use this for any API that you want to call.

    Args:
        method (str): The HTTP method to use.
        url (str): The URL to call.
        params (Dict[str, str], optional): The query parameters. Defaults to {}.
        data (Dict[str, str], optional): The data to send. Defaults to {}.
        json (Dict[str, str], optional): The JSON to send. Defaults to {}.
        headers (Dict[str, str], optional): The headers to send. Defaults to {}.
        cookies (Dict[str, str], optional): The cookies to send. Defaults to {}.
        auth (Dict[str, str], optional): The auth to send. Defaults to {}.
        timeout (float, optional): The timeout in seconds. Defaults to 0.
        max_retries (int, optional): The number of times to retry the request. Defaults to 3.
        retry_delay (int, optional): The number of seconds to wait between retries. Defaults to 1.

    Returns:
        Tuple[Tuple[str, int], Optional[Exception]]: The response text and status code, and the exception if there was one.
    """
    method = method.upper()
    if method not in _VALID_HTTP_METHODS:
        raise ValueError(f"method must be one of {_VALID_HTTP_METHODS}")

    def _fn():
        with requests.Session() as sess:
            out = sess.request(
                method,
                url,
                params=params,
                data=data,
                headers=headers,
                cookies=cookies,
                auth=auth,  # type: ignore
                timeout=None if not timeout else timeout,
                allow_redirects=True,
                json=json,
            )
        return out.text, out.status_code

    text, status_code = exponential_backoff(
        foo=_fn, max_retries=max_retries, retry_delay=retry_delay
    )
    return (text, status_code), None  # type: ignore


programatic_actions_registry.register(
    fn=call_api_requests,
    outputs={
        "text": (0,),
        "status_code": (1,),
    },
    node_id="call_api_requests",
    description="Call an API using the requests library",
)


# a few functions that do regex things


def regex_search(pattern: str, text: str) -> Tuple[List[str], Optional[Exception]]:
    """
    Perform a regex search on the text and get items in an array

    Args:
        pattern (str): The regex pattern to search for
        text (str): The text to search in

    Returns:
        Tuple[List[str], Optional[Exception]]: The list of items found
    """
    try:
        out = re.findall(pattern, text)
        return out, None
    except Exception as e:
        return [], e


programatic_actions_registry.register(
    fn=regex_search,
    outputs={
        "items": (0,),
    },
    node_id="regex_search",
    description="Perform a regex search on the text and get items in an array",
)


def regex_substitute(
    pattern: str, repl: str, text: str
) -> Tuple[str, Optional[Exception]]:
    """
    Perform a regex substitution on the text and get the result

    Args:
        pattern (str): The regex pattern to search for
        repl (str): The replacement string
        text (str): The text to search in

    Returns:
        Tuple[str, Optional[Exception]]: The substituted text and the exception if there was one
    """
    try:
        out = re.sub(pattern, repl, text)
        return out, None
    except Exception as e:
        return "", e


programatic_actions_registry.register(
    fn=regex_substitute,
    outputs={
        "text": (0,),
    },
    node_id="regex_substitute",
    description="Perform a regex substitution on the text and get the result",
)


def json_translator(
    data: Union[str, Dict[str, str]],
    resolver: Dict[str, str],
    default: str = "",
    return_only_value: bool = False,
) -> Tuple[str, Optional[Exception]]:
    """
    This simple function takes a json string or a python dictionary and translates it to the required output defined by
    the `resolver`. It is a dictionary that tells the location of the output that you want and the target locations.
    Here is a simple example on how you can use this:

    .. code-block:: python

        >>> x = {
        ...   "a": {
        ...     "b": [1, 2, 3],
        ...     "c": {
        ...       "d": "hello",
        ...       "e": "world",
        ...     }
        ...   },
        ...   "f": "foo",
        ... }
        >>> resolver = {
        ...   "x": ["a", "b", 0],
        ...   "y": ["a", "c", "d"],
        ...   "z": ["f"],
        ... }
        >>> json_translator(x, resolver)
        >>> {
        ...   "x": 1,
        ...   "y": "hello",
        ...   "z": "foo",
        ... }

    Note:
        If you pass `return_only_value=True`, then the output will be the value of the first key in the resolver. See
        below for an example:

    .. code-block:: python

        >>> json_translator(x, resolver, return_only_value=True)
        >>> 1

    Args:
        data (Union[str, Dict[str, Any]]): The data to be processed
        resolver (Dict[str, str], optional): The resolver dictionary. Defaults to {}.
        default (str, optional): The default value to be returned if the resolver fails. Defaults to "".
        return_only_value (bool, optional): If True, only the value is returned. Defaults to False.

    Returns:
        Tuple[str, Optional[Exception]]: The output and the exception if any
    """
    if type(data) == str:
        data = json.loads(data)
    out = {}
    for k, v in resolver.items():
        if isinstance(v, dict):
            _temp = {}
            for k1, v1 in v.items():
                _temp[k1] = get_value_by_keys(data, v1)
            out[k] = _temp
        else:
            out[k] = get_value_by_keys(data, v)
    if return_only_value:
        out = next(iter(out.items()))[1]
    out = default or out
    return json.dumps(out), None


programatic_actions_registry.register(
    fn=json_translator,
    outputs={
        "value": (0,),
    },
    node_id="json_translator",
    description="Extract a value from a JSON object using a list of keys",
)


def echo(message: str) -> Tuple[Dict[str, Dict[str, str]], Optional[Exception]]:
    return {"data": {"type": "text", "data": message}}, None


programatic_actions_registry.register(
    fn=echo,
    outputs={"message": (0,)},  # type: ignore
    node_id="chainfury-echo",
    description="I stared into the abyss and it stared back at me. Echoes the message, used for debugging",
)

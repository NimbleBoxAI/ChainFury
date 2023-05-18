"""
Functional components are the programatic components that are available to the fury
system. These are mostly for demo examples, we expect the user to register their
unique components into programatic_action_registry.
"""

import re
import requests
from typing import Any, List, Union, Tuple

from fury import programatic_actions_registry

# Call API: very basic always helpful


def call_api_requests(
    method: str,
    url: str,
    params: dict = {},
    data: dict = {},
    json: dict = {},
    headers: dict = {},
    cookies: dict = {},
    auth: dict = {},
    timeout: float = 0,
) -> Tuple[str, int]:
    with requests.Session() as sess:
        out = sess.request(
            method,
            url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=None if not timeout else timeout,
            allow_redirects=True,
            json=json,
        )
    return out.text, out.status_code


programatic_actions_registry.register(
    call_api_requests,
    "call_api_requests",
    "Call an API using the requests library",
)


# a few functions that do regex things


def regex_search(pattern: str, text: str) -> List[str]:
    return re.findall(pattern, text)


programatic_actions_registry.register(
    regex_search,
    "regex_search",
    "Perform a regex search on the text and get items in an array",
)


def regex_substitute(pattern: str, repl: str, text: str) -> str:
    return re.sub(pattern, repl, text)


programatic_actions_registry.register(
    regex_substitute,
    "regex_substitute",
    "Perform a regex substitution on the text and get the result",
)

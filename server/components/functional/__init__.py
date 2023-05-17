import requests
from typing import Any, List, Union, Tuple

from fury import programatic_actions_registry


def call_api_requests(
    method: str,
    url: str,
    params: Union[dict, None] = None,
    data: Union[dict, None] = None,
    json: Union[dict, None] = None,
    headers: Union[dict, None] = None,
    cookies: Union[dict, None] = None,
    auth: Union[dict, None] = None,
    timeout: float = None,
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
            timeout=timeout,
            allow_redirects=True,
            json=json,
        )
    return out.text, out.status_code


programatic_actions_registry.register(
    call_api_requests,
    "call_api_requests",
    "Call an API using the requests library",
)

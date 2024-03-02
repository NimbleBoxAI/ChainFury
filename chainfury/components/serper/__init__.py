# Copyright © 2023- Frello Technology Private Limited

import json
import requests
from typing import Dict, Tuple, Optional, List

from chainfury import (
    programatic_actions_registry,
    exponential_backoff,
    Secret,
    UnAuthException,
)
from chainfury.components.const import Env


VALID_SEARCH_TYPES = [
    "search",
    "images",
    "places",
    "news",
]


def serper_api(
    query: str,
    serper_api_key: Secret = Secret(""),
    search_type: str = "search",
    location: str = "in",
    locale: str = "en",
    autocorrect: bool = True,
    page: int = 1,
    num_per_page: int = 10,
    retry_count: int = 3,
    retry_delay: int = 1,
) -> Tuple[Tuple[Dict[str, str], int], Optional[Exception]]:
    """
    Search the web with Serper.

    **NOTE**: This action requires a Serper API key. You can get one for free at https://serper.dev.

    Here's a few types of responses that the different serper APIs return (this was written on 3rd July, 2023):

    .. code-block:: python

        >>> news_api
        {
            "news": [
                {
                    "date": "2 hours ago",
                    "imageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0KmSaKaJRif6f0wIBvRfnQfcQOXnoWWQ9ZM0VfTz9n6NXbCEUp76Nj-z1bw&s",
                    "link": "https://sg.news.yahoo.com/apple-makes-history-first-3-085543504.html",
                    "position": 1,
                    "snippet": "(Reuters) - Apple Inc become the first company in the world to reach a market value of $3 trillion, buoyed by hopes over its expansion in...",
                    "source": "Yahoo News Singapore",
                    "title": "Apple makes history as first $3 trillion company amid tech stock surge"
                }
            ],
            "searchParameters": {
                "autocorrect": true,
                "gl": "us",
                "hl": "en",
                "num": 10,
                "page": 1,
                "q": "apple inc",
                "type": "news"
            }
        }
        >>> search_api
        {
            "searchParameters": {
                "q": "apple inc",
                "gl": "us",
                "hl": "en",
                "num": 20,
                "autocorrect": false,
                "page": 3,
                "type": "search"
            },
            "organic": [
                {
                    "title": "Chennai, Tamil Nadu, India Weather Forecast - AccuWeather",
                    "link": "https://www.accuweather.com/en/in/chennai/206671/weather-forecast/206671",
                    "snippet": "Chennai, Tamil Nadu ; Current Weather. 4:17 PM. 82°F · RealFeel® 91° ; TODAY'S WEATHER FORECAST. 7/3. 83°Hi. RealFeel® 95° ; TONIGHT'S WEATHER FORECAST. 7/3. 78°Lo.",
                    "position": 1
                }
            ],
            "answerBox": {
                "title": "Chennai, Tamil Nadu, India / Weather",
                "answer": "87°F"
            },
            "knowledgeGraph": {
                "title": "Jeff Bezos",
                "type": "Executive Chairman of Amazon",
                "imageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTxFsGLOkNFB1vs2kvXM1_WNJZOwWHtdGaaLAnsHA&s=0",
                "description": "Jeffrey Preston Bezos is an American entrepreneur, media proprietor, and investor. He is the founder, executive chairman, and former president and CEO of Amazon, the world's largest e-commerce and cloud computing company.",
                "descriptionSource": "Wikipedia",
                "descriptionLink": "https://en.wikipedia.org/wiki/Jeff_Bezos",
                "attributes": {
                    "Born": "12 January 1964 (age 59 years), Albuquerque, New Mexico, United States",
                    "Net worth": "15,730 crores USD (2023)",
                    "Spouse": "MacKenzie Scott (m. 1993–2019)",
                    "Children": "Preston Bezos",
                    "Parents": "Ted Jorgensen, Miguel Bezos and Jacklyn Bezos",
                    "Height": "1.71 m",
                    "Nationality": "American"
                }
            }
            "peopleAlsoAsk": [
                {
                    "question": "What is the climate now in Chennai?",
                    "snippet": "The weather today in Chennai will be very hot with temperatures reaching 96°F.",
                    "title": "The local weather in Chennai today - Weather25.com",
                    "link": "https://www.weather25.com/asia/india/tamil-nadu/chennai?page=today"
                }
            ],
            "relatedSearches": [
                {
                    "query": "What is the weather in chennai this week"
                },
                {
                    "query": "Weather forecast Chennai cyclone"
                }
            ]
        }
        >>> image_api
        {
            "images": [
                {
                    "title": "Chennai weather forecast: Chennai, other parts of Tamil Nadu ...",
                    "imageUrl": "https://static.toiimg.com/photo/msid-71699845/71699845.jpg",
                    "imageWidth": 1200,
                    "imageHeight": 900,
                    "thumbnailUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTscW9XwTVb2S1aHCgaDHgvdTKHP6Vq8rAk4F9dm6YP8udSa6rZ&amp;s",
                    "thumbnailWidth": 259,
                    "thumbnailHeight": 194,
                    "source": "Times of India",
                    "domain": "timesofindia.indiatimes.com",
                    "link": "https://timesofindia.indiatimes.com/city/chennai/chennai-other-parts-of-tamil-nadu-likely-to-get-heavy-to-very-heavy-rain-for-next-three-days/articleshow/71699802.cms",
                    "position": 1
                }
            ],
            "searchParameters": {
                "q": "what is the weather in chennai?",
                "gl": "us",
                "hl": "en",
                "num": 20,
                "autocorrect": false,
                "page": 1,
                "type": "images"
            }
        }


    Args:
        query (str): The search query.
        serper_api_key (Secret): The Serper API key. Defaults to the value of SERPER_API_KEY environment variable.
        search_type (str): The type of search to perform. Must be one of "search", "images", "places", or "news".
        resolver (Dict[str, Union[str, List[str], Tuple[str, ...]]]): The keys to return in the output JSON.
        location (str): The location to search from. Defaults to "in".
        locale (str): The locale to search from. Defaults to "en".
        autocorrect (bool): Whether to autocorrect the query. Defaults to True.
        page (int): The page number to return. Defaults to 1.
        num_per_page (int): The number of results to return per page. Defaults to 10.
        retry_count (int): The number of times to retry the request. Defaults to 3.
        retry_delay (int): The number of seconds to wait between retries. Defaults to 1.

    Returns:
        dict: The search results.
    """
    if search_type not in VALID_SEARCH_TYPES:
        raise ValueError(f"search_type must be one of {VALID_SEARCH_TYPES}")
    if not serper_api_key:
        serper_api_key = Secret(Env.SERPER_API_KEY("")).value
    if not serper_api_key:
        raise Exception(
            "Serper API key not found. Please set SERPER_API_KEY environment variable or pass it as an argument."
        )

    def _fn():
        r = requests.post(
            f"https://google.serper.dev/search",
            headers={
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json",
            },
            json={
                "q": query,
                "gl": location,
                "hl": locale,
                "num": num_per_page,
                "autocorrect": autocorrect,
                "page": page,
                "type": search_type,
            },
        )
        if r.status_code == 401:
            raise UnAuthException(r.text)
        elif r.status_code == 403:
            raise Exception("Serper API key is invalid.")
        elif r.status_code != 200:
            raise Exception(
                f"Serper API returned status code {r.status_code}: {r.text}"
            )

        return r.json(), r.status_code

    try:
        api_resp, status_code = exponential_backoff(
            foo=_fn, max_retries=retry_count, retry_delay=retry_delay
        )
        return (api_resp, status_code), None  # type: ignore
    except Exception as e:
        return (None, None), e  # type: ignore


programatic_actions_registry.register(
    fn=serper_api,
    node_id="serper-api",
    description="Search the web with Serper",
    outputs={
        "text": (0,),
        "status_code": (1,),
    },
)

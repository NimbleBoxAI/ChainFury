# Copyright © 2023- Frello Technology Private Limited

from uuid import uuid4
from functools import lru_cache
from typing import List, Dict, Tuple, Optional, Union

try:
    from qdrant_client import models, QdrantClient

    QDRANT_CLIENT_INSTALLED = True
except ImportError:
    QDRANT_CLIENT_INSTALLED = False

from chainfury import Secret, memory_registry, logger
from chainfury.components.const import Env, ComponentMissingError

# https://qdrant.tech/documentation/concepts/filtering
# Must : "must" : AND
# Should : "should" : OR
# Must Not: "must_not" : NOT
# Match: =
# Match Any: IN
# Match Except: NOT IN


@lru_cache(maxsize=1)
def _get_qdrant_client(
    qdrant_url: Secret = Secret(), qdrant_api_key: Secret = Secret()
):
    """Create a qdrant client and cache it

    Args:
        qdrant_url (Secret, optional): qdrant url or set env var `QDRANT_API_URL`.
        qdrant_api_key (Secret, optional): qdrant api key or set env var `QDRANT_API_KEY`.

    Returns:
        qdrant_client.QdrantClient: qdrant client
    """
    qdrant_url = Secret(Env.QDRANT_API_URL(qdrant_url.value)).value  # type: ignore
    qdrant_api_key = Secret(Env.QDRANT_API_KEY(qdrant_api_key.value)).value  # type: ignore
    if not qdrant_url:
        raise Exception(
            "Qdrant URL is not set. Please pass `qdrant_url` or  env var `QDRANT_API_URL=<your_url>`"
        )
    if not qdrant_api_key:
        raise Exception(
            "Qdrant API KEY is not set. Please pass `qdrant_api_key` or  env var `QDRANT_API_KEY=<your_url>`"
        )
    logger.info("Creating Qdrant client")
    return QdrantClient(url=qdrant_url, api_key=qdrant_api_key)  # type: ignore


def qdrant_write(
    embeddings: List[List[float]],
    collection_name: str,
    qdrant_url: Secret = Secret(""),
    qdrant_api_key: Secret = Secret(""),
    extra_payload: List[Dict[str, str]] = [],
    wait: bool = True,
    create_if_not_present: bool = True,
    distance: str = "cosine",
) -> Tuple[str, Optional[Exception]]:
    """
    Write to the Qdrant DB using the Qdrant client. In order to use this, access via the `memory_registry`:

    Example:
        >>> from chainfury import memory_registry
        >>> mem = memory_registry.get_write("qdrant")
        >>> sentence = "C.P. Cavafy is widely considered the most distinguished Greek poet of the 20th century."
        >>> out, err = mem(
                {
                    "items": [sentence],
                    "extra_payload": [
                        {"data": sentence},
                    ],
                    "collection_name": "my_test_collection",
                    "embedding_model": "openai-embedding",
                    "create_if_not_present": True,
                }
            )
        >>> if err:
                print("TRACE:", out)
            else:
                print(out)

    Args:
        embeddings (List[List[float]]): list of embeddings
        collection_name (str): collection name
        qdrant_url (Secret, optional): qdrant url or set env var `QDRANT_API_URL`.
        qdrant_api_key (Secret, optional): qdrant api key or set env var `QDRANT_API_KEY`.
        extra_payload (List[Dict[str, str]], optional): extra payload. Defaults to [].
        wait (bool, optional): wait for the response. Defaults to True.
        create_if_not_present (bool, optional): create collection if not present. Defaults to True.
        distance (str, optional): distance metric. Defaults to "cosine".

    Returns:
        Tuple[str, Optional[Exception]]: status and error
    """
    # client check
    if not QDRANT_CLIENT_INSTALLED:
        raise ComponentMissingError(
            "Qdrant client is not installed. Please install it with `pip install qdrant-client`"
        )

    # checks
    if not (len(embeddings) and len(embeddings[0]) and type(embeddings[0][0]) == float):
        raise Exception("Embeddings should be a list of lists of floats")
    if extra_payload and len(extra_payload) != len(embeddings):
        raise Exception("Length of extra_payload should be equal to embeddings")

    client: QdrantClient = _get_qdrant_client(qdrant_url, qdrant_api_key)  # type: ignore

    # next we create points and upsert them into the DB
    points = []
    for i, embedding in enumerate(embeddings):
        payload = {}
        if extra_payload:
            payload = extra_payload[i]
        points.append(models.PointStruct(id=str(uuid4()), payload=payload, vector=embedding))  # type: ignore
    batch = models.Batch(  # type: ignore
        ids=[point.id for point in points],
        vectors=[point.vector for point in points],
        payloads=[point.payload for point in points],
    )

    def _insert():
        try:
            result = client.upsert(
                collection_name=collection_name,
                points=batch,
                wait=wait,
            )
        except Exception as e:
            return e.content, e  # type: ignore
        return result.status.lower(), None

    status, err = _insert()
    if err and err.status_code == 404 and create_if_not_present:  # type: ignore
        collection = client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(  # type: ignore
                size=len(embeddings[0]),
                distance=getattr(models.Distance, distance.upper()),  # type: ignore
            ),
        )
        logger.info(f"Created collection {collection}")
        status, err = _insert()
    return status, err


memory_registry.register_write(
    component_name="qdrant",
    fn=qdrant_write,
    outputs={"status": 0},
    vector_key="embeddings",
    description="Write to the Qdrant DB using the Qdrant client",
)


def qdrant_read(
    embeddings: List[List[float]],
    collection_name: str,
    cutoff_score: float = 0.0,
    top: int = 5,
    limit: int = 0,
    offset: int = 0,
    filters: Dict[str, Dict[str, str]] = {},
    qdrant_url: Secret = Secret(""),
    qdrant_api_key: Secret = Secret(""),
    qdrant_search_hnsw_ef: int = 0,
    qdrant_search_exact: bool = False,
    batch_search: bool = False,
) -> Tuple[Dict[str, List[Dict[str, Union[float, int]]]], Optional[Exception]]:
    """
    Read from the Qdrant DB using the Qdrant client. In order to use this access via the `memory_registry`:

    Example:
        >>> from chainfury import memory_registry
        >>> mem = memory_registry.get_read("qdrant")
        >>> sentence = "Who was the Cafavy?"
        >>> out, err = mem(
                {
                    "items": [sentence],
                    "collection_name": "my_test_collection",
                    "embedding_model": "openai-embedding"
                }
            )
        >>> if err:
                print("TRACE:", out)
            else:
                print(out)

    Note:
        `batch_search` is not implemented yet. There's some issues from the `qdrant_client` library.

    Args:
        embeddings (List[List[float]]): list of embeddings
        collection_name (str): collection name
        cutoff_score (float, optional): cutoff score. Defaults to 0.0.
        limit (int, optional): limit. Defaults to 3.
        offset (int, optional): offset. Defaults to 0.
        qdrant_url (Secret, optional): qdrant url or set env var `QDRANT_API_URL`.
        qdrant_api_key (Secret, optional): qdrant api key or set env var `QDRANT_API_KEY`.
        qdrant_search_hnsw_ef (int, optional): qdrant search beam size, the larger the beam size the more accurate the search,
            if not set uses default value.
        qdrant_search_exact (bool, optional): qdrant search exact. Defaults to False.
        batch_search (bool, optional): batch search. Defaults to False.

    Returns:
        Tuple[List[Dict[str, Union[float, int]]], Optional[Exception]]: list of results and error
    """
    # client check
    if not QDRANT_CLIENT_INSTALLED:
        raise ComponentMissingError(
            "Qdrant client is not installed. Please install it with `pip install qdrant-client`"
        )

    # checks
    if not (len(embeddings) and len(embeddings[0]) and type(embeddings[0][0]) == float):
        raise Exception("Embeddings should be a list of lists of floats")
    if batch_search:
        raise NotImplementedError("Batch search is not implemented yet")
    if not batch_search and len(embeddings) > 1:
        raise Exception(
            "Batch search is not enabled, but multiple embeddings are passed"
        )
    if not top and not limit:
        raise Exception("Either top or limit should be set")

    client: QdrantClient = _get_qdrant_client(qdrant_url, qdrant_api_key)  # type: ignore

    search_params = models.SearchParams()  # type: ignore
    if qdrant_search_hnsw_ef:
        search_params.hnsw_ef = qdrant_search_hnsw_ef
    if qdrant_search_exact:
        search_params.exact = qdrant_search_exact

    if batch_search:
        # this is not implemented, this fails when we try to pass a list of vectors
        search_queries = [
            models.SearchRequest(
                vector=x, limit=limit, offset=offset, params=search_params
            )
            for x in embeddings
        ]
        out = client.search_batch(
            collection_name=collection_name,
            requests=search_queries,
        )
        res = [[_x.dict(skip_defaults=False) for _x in x] for x in out]  # type: ignore

    query_filter = None
    if filters:
        query_filter = models.Filter(**filters)  # type: ignore

    out = client.search(
        collection_name=collection_name,
        query_vector=embeddings[0],
        query_filter=query_filter,
        limit=max(limit, top),
        offset=offset,
        search_params=search_params,
    )
    out = [x for x in out if x.score > cutoff_score]
    res = [_x.dict(skip_defaults=False) for _x in out]  # type: ignore
    return {"data": res}, None


memory_registry.register_read(
    component_name="qdrant",
    fn=qdrant_read,
    outputs={"items": 0},
    vector_key="embeddings",
    description="Function to read from the Qdrant DB using the Qdrant client",
)


# helper functions


def recreate_collection(collection_name: str, embedding_dim: int) -> bool:
    """
    Deletes and recreates a collection

    Note:
        This will delete all the data in the collection, use with caution

    Args:
        collection_name (str): collection name
        embedding_dim (int): embedding dimension

    Returns:
        bool: success
    """
    client: QdrantClient = _get_qdrant_client()  # type: ignore
    return client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(  # type: ignore
            size=embedding_dim,
            distance=models.Distance.COSINE,  # type: ignore
        ),
        optimizers_config=models.OptimizersConfigDiff(  # type: ignore
            indexing_threshold=0,
        ),
    )


def enable_indexing(collection_name: str, indexing_threshold: int = 20000) -> bool:
    """
    Enable indexing for a collection, use this in conjunction with `disable_indexing`. Read more
    `here <https://qdrant.tech/documentation/tutorials/bulk-upload/#upload-directly-to-disk>`_.

    Example:
        >>> from chainfury.components.qdrant import enable_indexing, disable_indexing, qdrant_write
        >>> disable_indexing("my_collection")
        >>> qdrant_write([[1, 2, 3] for _ in range(100)], "my_collection")
        >>> enable_indexing("my_collection")


    Args:
        collection_name (str): collection name
        indexing_threshold (int, optional): indexing threshold. Defaults to 20000.

    Returns:
        bool: success
    """
    client: QdrantClient = _get_qdrant_client()  # type: ignore
    return client.update_collection(
        collection_name=collection_name,
        optimizer_config=models.OptimizersConfigDiff(  # type: ignore
            indexing_threshold=indexing_threshold,
        ),
    )


def disable_indexing(collection_name: str):
    """
    Disable indexing for a collection, use this in conjunction with `enable_indexing`. Read more
    `here <https://qdrant.tech/documentation/tutorials/bulk-upload/#upload-directly-to-disk>`_.

    Args:
        collection_name (str): collection name

    Returns:
        bool: success
    """
    client: QdrantClient = _get_qdrant_client()  # type: ignore
    return client.update_collection(
        collection_name=collection_name,
        optimizer_config=models.OptimizersConfigDiff(  # type: ignore
            indexing_threshold=0,
        ),
    )

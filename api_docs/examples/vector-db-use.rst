Vector Database (β Beta)
========================

A vector database is a type of database that stores data in a vector format, meaning that each data point is represented
as a vector in a high-dimensional space. This allows for efficient querying and processing of data using vector-based
algorithms, such as vector similarity searches and clustering. Vector databases are particularly useful for applications
that involve large amounts of text, image, or audio data, such as natural language processing, computer vision, and
speech recognition.

Embeddings are commonly used for:

* Search (where results are ranked by relevance to a query string)
* Clustering (where text strings are grouped by similarity)
* Recommendations (where items with related text strings are recommended)
* Anomaly detection (where outliers with little relatedness are identified)
* Diversity measurement (where similarity distributions are analyzed)
* Classification (where text strings are classified by their most similar label)

Demo Working Code
-----------------

.. code-block:: python

  >>> # do the imports
  >>> from chainfury import memory_registry
  >>> from pprint import pprint

  >>> # get the write node
  >>> mem = memory_registry.get_write("qdrant")
  >>> print(mem)
  FuryNode{ ('qdrant-write', 'memory') [
        Var(*name='embeddings', type='array', items=[Var(name='', type='array', items=[Var(name='', type='number', items=[], additionalProperties=[])], additionalProperties=[])], additionalProperties=[]),
        Var(*name='collection_name', type='string', items=[], additionalProperties=[]),
        Var(*name='items', type='[Var(name='', type='string', items=[], additionalProperties=[]), Var(name='', type='array', items=[Var(name='', type='string', items=[], additionalProperties=[])], additionalProperties=[])]', items=[], additionalProperties=[]),
        Var(*name='embedding_model', type='string', items=[], additionalProperties=[]),
  ] (13) => (1) [
        Var(name='status', type='string', items=[], additionalProperties=[]),
  ] }

  >>> # create a query document pair, we are talking about the famous Greek Poet C.P. Cavafy
  >>> sentence = "C.P. Cavafy is widely considered the most distinguished Greek poet of the 20th century. He was born in Alexandria, Egypt, where his Greek parents had settled in the mid-1850s. Cavafy’s father was an importer-exporter whose business responsibilities frequently led him to the port city of Liverpool, England. Cavafy’s father died in 1870, and the business he left in Alexandria proved insufficiently profitable for Cavafy’s mother and eight siblings. The family consequently moved to Liverpool, where the eldest sons assumed control of the family's business operations."
  >>> sentence_q = "Who was the Cafavy?"

  >>> # write in a collection
  >>> out, err = mem(
  ...     {
  ...         "items": [sentence],
  ...         "extra_payload": [
  ...             {"data": sentence},
  ...         ],
  ...         "collection_name": "my_test_collection",
  ...         "embedding_model": "openai-embedding",
  ...         "create_if_not_present": True,
  ...     }
  ... )
  [2023-07-31T13:45:25+0530] [INFO] [__init__.py:27] Creating Qdrant client
  >>> if err:
  ...     print("TRACE:", out)
  ... else:
  ...     print(out)
  {'status': 'completed'}

  >>> # to query first get the query node
  >>> mem  = memory_registry.get_read("qdrant")
  >>> print(mem)
  FuryNode{ ('qdrant-read', 'memory') [
        Var(*name='embeddings', type='array', items=[Var(name='', type='array', items=[Var(name='', type='number', items=[], additionalProperties=[])], additionalProperties=[])], additionalProperties=[]),
        Var(*name='collection_name', type='string', items=[], additionalProperties=[]),
        Var(*name='items', type='[Var(name='', type='string', items=[], additionalProperties=[]), Var(name='', type='array', items=[Var(name='', type='string', items=[], additionalProperties=[])], additionalProperties=[])]', items=[], additionalProperties=[]),
        Var(*name='embedding_model', type='string', items=[], additionalProperties=[]),
  ] (15) => (1) [
        Var(name='items', type='object', items=[], additionalProperties=Var(name='', type='array', items=[Var(name='', type='object', items=[], additionalProperties=Var(name='', type='[Var(name='', type='number', items=[], additionalProperties=[]), Var(name='', type='number', items=[], additionalProperties=[])]', items=[], additionalProperties=[]))], additionalProperties=[])),
  ] }

  >>> # read from the collection
  >>> out, err = mem(
  ...     {
  ...         "items": [sentence_q],
  ...         "collection_name": "my_test_collection",
  ...         "embedding_model": "openai-embedding",
  ...         "limit": 1,
  ...     }
  ... )
  >>> if err:
  ...    print("TRACE:", out)
  ... else:
  ...    print(out)
  {'items': {'data': [{'id': '5a33121d-3f7c-4540-a7ba-bf28c6135576',
                     'payload': {'data': 'C.P. Cavafy is widely considered the '
                                         'most distinguished Greek poet of the '
                                         '20th century. He was born in '
                                         'Alexandria, Egypt, where his Greek '
                                         'parents had settled in the '
                                         'mid-1850s. Cavafy’s father was an '
                                         'importer-exporter whose business '
                                         'responsibilities frequently led him '
                                         'to the port city of Liverpool, '
                                         'England. Cavafy’s father died in '
                                         '1870, and the business he left in '
                                         'Alexandria proved insufficiently '
                                         'profitable for Cavafy’s mother and '
                                         'eight siblings. The family '
                                         'consequently moved to Liverpool, '
                                         'where the eldest sons assumed '
                                         "control of the family's business "
                                         'operations.'},
                     'score': 0.80718714,
                     'vector': None,
                     'version': 16}]}}

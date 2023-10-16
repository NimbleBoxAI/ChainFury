Components List
===============

.. this is a jinja template document, run scripts/list_builtins.py to generate components-list.rst

There are several components that are shipped with the ``chainfury``. You can find how to access the underlying function
via the `components page`_.

.. code-block::python

  # load the registries you can do these imports
  from chainfury import programatic_actions_registry, ai_actions_registry

Programatic Actions
-------------------

Programatic means that these are generally not an LLM call rather something more standard like calling an API,
transforming the data, etc.


* `serper-api` - Search the web with Serper. Copy: ``programatic_actions_registry.get("serper-api")``

* `call_api_requests` - Call an API using the requests library. Copy: ``programatic_actions_registry.get("call_api_requests")``

* `regex_search` - Perform a regex search on the text and get items in an array. Copy: ``programatic_actions_registry.get("regex_search")``

* `regex_substitute` - Perform a regex substitution on the text and get the result. Copy: ``programatic_actions_registry.get("regex_substitute")``

* `json_translator` - Extract a value from a JSON object using a list of keys. Copy: ``programatic_actions_registry.get("json_translator")``


AI Action Components
--------------------

These actions generally take the input, create a custom prompt, call the Model and respond back with the result.


* `hello-world` - Python function loaded from a file used as an AI action. Copy: ``ai_actions_registry.get("hello-world")``

* `deep-rap-quote` - J-type action will write a deep poem in the style of a character. Copy: ``ai_actions_registry.get("deep-rap-quote")``


Memory Components
-----------------

Memory components are used to store data, which can be a Vector DB or Redis, etc.


* `qdrant-write` - Write to the Qdrant DB using the Qdrant client. Copy: ``memory_registry.get_write("qdrant-write")``

* `qdrant-read` - Function to read from the Qdrant DB using the Qdrant client. Copy: ``memory_registry.get_read("qdrant-read")``


Model Components
----------------

Model are the different GenAI models that can be used from the ``chainfury``.


* `stability-text-to-image` - Generate a new image from a text prompt. Copy: ``model_registry.get("stability-text-to-image")``

* `chatnbx` - Chat with the ChatNBX API with OpenAI compatability, see more at https://chat.nbox.ai/. Copy: ``model_registry.get("chatnbx")``

* `nbx-deploy` - Call NimbleBox LLMOps deploy API. Copy: ``model_registry.get("nbx-deploy")``

* `openai-completion` - Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position. Copy: ``model_registry.get("openai-completion")``

* `openai-chat` - Given a list of messages describing a conversation, the model will return a response. Copy: ``model_registry.get("openai-chat")``

* `openai-embedding` - Given a list of messages create embeddings for each message. Copy: ``model_registry.get("openai-embedding")``


.. all the links are here

.. _components page: https://qdrant.tech/documentation/tutorials/bulk-upload/#upload-directly-to-disk

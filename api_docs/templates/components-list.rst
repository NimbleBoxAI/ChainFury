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

{% for component in pc %}
* `{{ component.id }}` - {{ component.description }}
{% endfor %}

AI Action Components
--------------------

These actions generally take the input, create a custom prompt, call the Model and respond back with the result.

{% for component in ac %}
* `{{ component.id }}` - {{ component.description }}
{% endfor %}

Memory Components
-----------------

Memory components are used to store data, which can be a Vector DB or Redis, etc.

{% for component in mc %}
* `{{ component.id }}` - {{ component.description }}
{% endfor %}

Model Components
----------------

Model are the different GenAI models that can be used from the ``chainfury``.

{% for component in moc %}
* `{{ component.id }}` - {{ component.description }}
{% endfor %}

.. all the links are here

.. _components page: https://qdrant.tech/documentation/tutorials/bulk-upload/#upload-directly-to-disk


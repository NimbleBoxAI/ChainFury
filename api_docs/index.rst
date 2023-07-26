.. ChainFury documentation master file, created by
   sphinx-quickstart on Thu Jun 22 14:12:55 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ChainFury
=========

Build complex chat apps using LLMs in 4 clicks ⚡️ `Try it out here <https://chainfury.nbox.ai/>`__

ChainFury is a powerful tool that simplifies the creation and management of chains of prompts, making it easier to build
complex chat applications using LLMs.

.. code-block:: bash

   # install the chainfury engine and client
   pip install chainfury

   # you can install the self hosted server as follows
   pip install chainfury_server
   python3 -m chainfury_server


Read the latest blog posts:

* `ChainFury - Create LLM ChatBots in 4 clicks! <https://medium.com/@chandranih/chainfury-create-llm-chatbots-in-4-clicks-3663538db8c6>`__ - to learn more
* `Why the Fury? Building a new flow engine from scratch <https://blog.nimblebox.ai/new-flow-engine-from-scratch>`__ - to understand the motivation behind ChainFury
* `Fury Actions <https://nimblebox.ai/blog/fury-actions>`__ - to understand how `fury` actions work


.. toctree::
   :maxdepth: 2
   :caption: Contents

   install
   usage

.. toctree::
   :maxdepth: 4
   :caption: Contents

   examples/vector-db-use

.. toctree::
   :maxdepth: 2
   :caption: Python APIs

   source/chainfury.agent
   source/chainfury.cli
   source/chainfury.base
   source/chainfury.client
   source/chainfury.utils

.. toctree::
   :maxdepth: 2
   :caption: Integrations

   source/chainfury.components.const
   source/chainfury.components

.. toctree::
   :maxdepth: 2
   :caption: Server

   cf_server/chainfury_server.api
   cf_server/chainfury_server.commons
   cf_server/chainfury_server.database_utils
   cf_server/chainfury_server.engines
   cf_server/chainfury_server.plugins

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

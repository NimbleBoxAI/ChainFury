Installing ChainFury
====================

There are many ways to install and run the `chainfury` system the simplest of them all is `pip install chainfury`.

:py:mod:`chainfury.components.const.Env` contains all the supported environment variables.

PyPi
----

The simplest way to start using `chainfury` is to use `pip`:

.. code-block:: bash

    pip install chainfury
    pip install chainfury_server
    python3 -m chainfury_server

Docker
------

Docker is the simplest way to start serving chainfury internally. This can be done using the following commands:

.. code-block:: bash

    docker build . -f Dockerfile -t chainfury
    docker run -p 8000:8000 chainfury

    # to pass any env config
    docker run --env KEY=VALUE -p 8000:8000 chainfury

    # to connect to your DB
    docker run -it -E CFS_DATABASE="mysql+pymysql://<user>:<password>@127.0.0.1:3306/<database>" -p 8000:8000 chainfury

Checkout all the:
- `component` environment variables `here <https://nimbleboxai.github.io/ChainFury/source/chainfury.components.const.html#chainfury.components.const.Env>`__
- `chainfury` specific variables `here <https://nimbleboxai.github.io/ChainFury/source/chainfury.utils.html#chainfury.utils.CFEnv>`__
- `chainfury_server` specific variables `here <https://nimbleboxai.github.io/ChainFury/cf_server/chainfury_server.commons.config.html#chainfury_server.commons.config.Env>`__

Build from Source
-----------------

ChainFury repo ships with the Next.js client code, python `fastapi` server and the `chainfury` package that powers the
fury engine. To build the entire system you can run the following commands:

.. code-block:: bash

    # clone the repo
    git clone https://github.com/NimbleBoxAI/ChainFury
    cd ChainFury
    python3 -m venv venv
    source venv/bin/activate

    sudo apt update

    #Install npm
    sudo apt install npm

    #Install Node.js
    sudo apt install -y nodejs #Install version >= 14.0

    #Install Yarn
    sudo npm install -g yarn   #install yarn globally

    # build the client
    sh scripts/build_and_copy.sh

    # setup the server env
    pip install setuptools
    pip install -e .          # editable install the chainfury
    cd server
    pip install -e .          # editable install the chainfury_server

    # to start the server
    cd chainfury_server
    python3 server.py

    #

Installing ChainFury
====================

There are many ways to install and run the `chainfury` system the simplest of them all is `pip install chainfury`.

:py:mod:`chainfury.components.const.Env` contains all the supported environment variables.

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

Build from Source
-----------------

ChainFury repo ships with the Next.js client code, python `fastapi` server and the `chainfury` package that powers the
fury engine. To build the entire system you can run the following commands:

.. code-block:: bash

    # clone the repo
    git clone https://github.com/NimbleBoxAI/ChainFury
    ch ChainFury

    # build the client
    cd client
    yarn install
    yarn build
    cd ..

    # move the files to the server code
    cp -r client/dist/ server/static/
    mkdir -p ./server/templates
    cp ./client/dist/index.html ./server/templates/index.html

    # setup the server env
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd server

    # start the server: recommended approach
    python3 server.py --port 8000

    # to start using uvicorn: be careful with workers
    python3 -m uvicorn app:app --log-level=debug --host 0.0.0.0 --port 8000 --workers 2


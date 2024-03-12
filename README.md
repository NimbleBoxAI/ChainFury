# 🦋 NimbleBox ChainFury

[![linkcheck](https://img.shields.io/badge/Workflow-Passing-darkgreen)](https://github.com/NimbleBoxAI/ChainFury/actions)
[![Downloads](https://static.pepy.tech/badge/chainfury)](https://pepy.tech/project/chainfury)
[![linkcheck](https://img.shields.io/badge/Site-🦋ChainFury-lightblue)](https://chainfury.nbox.ai)
[![License: Apache](https://img.shields.io/badge/License-Apache%20v2.0-red)](https://github.com/NimbleBoxAI/ChainFury/blob/main/LICENSE) 
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/NimbleBoxAI.svg?style=social&label=Follow%20%40NimbleBoxAI)](https://twitter.com/NimbleBoxAI)
[![](https://dcbadge.vercel.app/api/server/KhF38hrAJ2?compact=true&style=flat)](https://discord.com/invite/KhF38hrAJ2)

```
  ___ _         _       ___
 / __| |_  __ _(_)_ _  | __|  _ _ _ _  _ 
| (__| ' \/ _` | | ' \ | _| || | '_| || |
 \___|_||_\__,_|_|_||_||_| \_,_|_|  \_, |
                                     |__/
e0 a4 b8 e0 a4 a4 e0 a5 8d e0 a4 af e0 a4
ae e0 a5 87 e0 a4 b5 20 e0 a4 9c e0 a4 af
            e0 a4 a4 e0 a5 87
```

🦋 The open source chaining engine behind [Tune Chat](https://chat.tune.app) and [Tune Studio](https://studio.tune.app).

# Read the [Docs](https://nimbleboxai.github.io/ChainFury/index.html)

The documentation page contains all the information on using `chainfury` and `chainfury_server`.

# Looking for Inspirations?

Here's a few example to get your journey started on Software 2.0:

- 📚 Retrieval Augmented Generation (RAG): Load a PDF and ask it questions, read [docs](https://nimbleboxai.github.io/ChainFury/examples/qa-rag.html)
- 🏞️ Image generation using Stability: Generate your world, read [here](https://nimbleboxai.github.io/ChainFury/examples/stability-apis.html)
- 🔐 Private Storage: Privately store the data on AWS S3, read [privacy](https://nimbleboxai.github.io/ChainFury/examples/storing-private-data.html)

# Installation

There are two separate packages built into this repository, first is `chainfury` which contains the fury-engine for running
the DAGs and `chainfury_server` which contains the self hosted server for the GUI.

``` bash
pip install chainfury
pip install chainfury_server

# to launch the server
python3 -m chainfury_server
```

### Run Docker

Easiest way to run the server is to use docker. You can use the following command to run ChainFury:

```bash
docker build . -f Dockerfile -t chainfury:latest
docker run -p 8000:8000 chainfury:latest
```

To pass any env variables you can use the command:

```bash
docker run --env ENV_KEY=ENV_VALUE -p 8000:8000 chainfury:latest
```

Checkout all the:
- `component` environment variables [here](https://nimbleboxai.github.io/ChainFury/source/chainfury.components.const.html#chainfury.components.const.Env)
- `chainfury` specific variables [here](https://nimbleboxai.github.io/ChainFury/source/chainfury.utils.html#chainfury.utils.CFEnv)
- `chainfury_server` specific variables [here](https://nimbleboxai.github.io/ChainFury/cf_server/chainfury_server.commons.config.html#chainfury_server.commons.config.Env)

### From Source

Here's a breakdown of folder:

- `chainfury/` contains the chainfury engine
- `server/` contains the chainfury server
- `client/` contains the frontend code for the GUI
- `api_docs/` contains the documentation

To build the entire system from scratch follow these steps:

```bash
git clone https://github.com/NimbleBoxAI/ChainFury
cd ChainFury
python3 -m venv venv
source venv/bin/activate
```

You will need to have `yarn` installed to build the frontend and move it to the correct location on the server

```bash
sh stories/build_and_copy.sh
```

Once the static files are copied we can now proceed to install dependecies:

```bash
pip install -e .          # editable install the chainfury
pip install -e server/.   # editable install the chainfury_server
python3 -m chainfury_server
```

You can now visit [localhost:8000](http://localhost:8000/ui/) to see the GUI and sign in with the default username password `admin:admin`.

### Tests

There are a few test cases for super hard problems like `get_kv` which checks the `chainfury.base.get_value_by_keys` function.

```bash
python3 -m tests -v
```

# Contibutions

ChainFury is an open-source project used in production. We are open to contributions to the project in the form of features,
infrastructure or documentation.

- If you're looking for help with your code, hop onto [Discord](https://discord.com/invite/KhF38hrAJ2), so that community can help you get to answer faster.
- We would appreciate help towareds writing more tests, see what we have in [tests folder](./tests/)

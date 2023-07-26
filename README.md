# 🦋 NimbleBox ChainFury

[![linkcheck](https://img.shields.io/badge/Workflow-Passing-darkgreen)](https://github.com/NimbleBoxAI/ChainFury/actions)
[![Downloads](https://static.pepy.tech/badge/chainfury)](https://pepy.tech/project/chainfury)
[![linkcheck](https://img.shields.io/badge/Site-🦋ChainFury-lightblue)](https://chainfury.nbox.ai)
[![License: Apache](https://img.shields.io/badge/License-Apache%20v2.0-red)](https://github.com/NimbleBoxAI/ChainFury/blob/main/LICENSE) 
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/NimbleBoxAI.svg?style=social&label=Follow%20%40NimbleBoxAI)](https://twitter.com/NimbleBoxAI)
[![](https://dcbadge.vercel.app/api/server/KhF38hrAJ2?compact=true&style=flat)](https://discord.com/invite/KhF38hrAJ2)

🦋 Build complex chat apps using LLMs in 4 clicks ⚡️ [Try it out here](https://chainfury.nbox.ai/). Used in production by [chat.nbox.ai](https://chat.nbox.ai).

# Read the [Docs](https://nimbleboxai.github.io/ChainFury/index.html)

The documentation page contains all the information on using `chainfury` and `chainfury_server`.

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
pip install setuptools
pip install -e .          # editable install the chainfury
cd server
pip install -e .          # editable install the chainfury_server
```

To start you can now do:

```bash
cd chainfury_server
python3 server.py
```

You can now visit [localhost:8000](http://localhost:8000/ui/) to see the GUI.

# Contibutions

ChainFury is an open-source project used in production. We are open to contributions to the project in the form of features,
infrastructure or documentation.

- Our [issues](https://github.com/NimbleBoxAI/ChainFury/issues) page is kept up to date with bugs, improvements, and feature requests.

- If you're looking for help with your code, hop onto [GitHub Discussions board](https://github.com/NimbleBoxAI/ChainFury/discussions) or
[Discord](https://discord.com/invite/KhF38hrAJ2), so that more people can benefit from it.

- **Describing your issue:** Try to provide as many details as possible. What exactly goes wrong? How is it failing?
Is there an error? "XY doesn't work" usually isn't that helpful for tracking down problems. Always remember to include
the code you ran and if possible, extract only the relevant parts and don't just dump your entire script. This will make
it easier for us to reproduce the error.

- **Sharing long blocks of code or logs:** If you need to include long code, logs or tracebacks, you can wrap them in
`<details>` and `</details>`. This [collapses the content](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details)
so it only becomes visible on click, making the issue easier to read and follow.


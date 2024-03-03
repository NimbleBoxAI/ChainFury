# Copyright © 2023- Frello Technology Private Limited

import os
import sys
import json
from fire import Fire

from chainfury import Chain
from chainfury.version import __version__
from chainfury.components import all_items
from chainfury.core import model_registry, programatic_actions_registry, memory_registry


def run(
    chain: str,
    inp: str,
    stream: bool = False,
    print_thoughts: bool = False,
    f=sys.stdout,
):
    """
    Run a chain with input and write the outputs.

    Args:
        chain (str): This can be one of json filepath (e.g. "/chain.json"), json string (e.g. '{"id": "99jcjs9j2", ...}'),
            chain id (e.g. "99jcjs9j2")
        inp (str): This can be one of json filepath (e.g. "/input.json"), json string (e.g. '{"foo": "bar", ...}')
        stream (bool, optional): Whether to stream the output. Defaults to False.
        print_thoughts (bool, optional): Whether to print thoughts. Defaults to False.
        f (file, optional): File to write the output to. Defaults to `sys.stdout`.

    Examples:
        >>> $ cf run ./sample.json {"foo": "bar"}
    """
    # validate inputs
    if isinstance(inp, str):
        if os.path.exists(inp):
            with open(inp, "r") as f:
                inp = json.load(f)
        else:
            try:
                inp = json.loads(inp)
            except Exception as e:
                raise ValueError(
                    "Input must be a valid json string or a json file path"
                )
    assert isinstance(inp, dict), "Input must be a dict"

    # create chain
    chain_obj = None
    if isinstance(chain, str):
        if os.path.exists(chain):
            with open(chain, "w") as f:
                chain = json.load(f)
        if len(chain) == 8:
            chain_obj = Chain.from_id(chain)
        else:
            chain = json.loads(chain)
    elif isinstance(chain, dict):
        chain_obj = Chain.from_dict(chain)
    assert chain_obj is not None, "Chain not found"

    # output
    if isinstance(f, str):
        f = open(f, "w")

    # run the chain
    if stream:
        cf_response_gen = chain_obj.stream(inp, print_thoughts=print_thoughts)
        for ir, done in cf_response_gen:
            if not done:
                f.write(json.dumps(ir) + "\n")
    else:
        out, buffer = chain_obj(inp, print_thoughts=print_thoughts)
        for k, v in buffer.items():
            f.write(json.dumps({k: v}) + "\n")

    # close file
    f.close()


class __CLI:
    info = rf"""
  ___ _         _       ___
 / __| |_  __ _(_)_ _  | __|  _ _ _ _  _ 
| (__| ' \/ _` | | ' \ | _| || | '_| || |
 \___|_||_\__,_|_|_||_||_| \_,_|_|  \_, |
                                     |__/
e0 a4 b8 e0 a4 a4 e0 a5 8d e0 a4 af e0 a4
ae e0 a5 87 e0 a4 b5 20 e0 a4 9c e0 a4 af
            e0 a4 a4 e0 a5 87


cf_version: {__version__}

🦋 The FOSS chaining engine behind chat.tune.app

A powerful way to program for the "Software 2.0" era. Read more:

- https://tunehq.ai
- https://chat.tune.app
- https://studio.tune.app
🌟 us on https://github.com/NimbleBoxAI/ChainFury

Build with ♥️  by Tune AI from the Koro coast 🌊 Chennai, India
"""

    comp = {
        "all": lambda: print(all_items),
        "model": {
            "list": list(model_registry.get_models()),
            "all": model_registry.get_models(),
            "get": model_registry.get,
        },
        "prog": {
            "list": list(programatic_actions_registry.get_nodes()),
            "all": programatic_actions_registry.get_nodes(),
        },
        "memory": {
            "list": list(memory_registry.get_nodes()),
            "all": memory_registry.get_nodes(),
        },
    }
    run = run


def main():
    Fire(__CLI)

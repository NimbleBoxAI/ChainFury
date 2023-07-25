import os
import sys
import json
from fire import Fire

from chainfury import Chain
from chainfury.utils import logger
from chainfury.client import get_client
from chainfury.version import __version__
from chainfury.components import all_items
from chainfury.agent import model_registry, programatic_actions_registry, memory_registry


def help():
    print(
        """
🦋 Welcome to ChainFury Engine!

A powerful way to program for the "Software 2.0" era. Read more:

- https://blog.nimblebox.ai/new-flow-engine-from-scratch
- https://blog.nimblebox.ai/fury-actions
- https://gist.github.com/yashbonde/002c527853e04869bfaa04646f3e0974

🌟 us on https://github.com/NimbleBoxAI/ChainFury

Build with ♥️  by NimbleBox.ai

🌊 Chennai, India
"""
    )


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
            inp = json.loads(inp)
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


def main():
    Fire(
        {
            "comp": {
                "all": lambda: print(all_items),
                "model": {
                    "list": list(model_registry.get_models()),
                    "all": model_registry.get_models(),
                },
                "prog": {
                    "list": list(programatic_actions_registry.get_nodes()),
                    "all": programatic_actions_registry.get_nodes(),
                },
                "memory": {
                    "list": list(memory_registry.get_nodes()),
                    "all": memory_registry.get_nodes(),
                },
            },
            "help": help,
            "run": run,
            "version": lambda: print(
                f"""ChainFury 🦋 Engine

chainfury=={__version__}
"""
            ),
        }
    )

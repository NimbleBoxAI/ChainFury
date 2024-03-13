# Copyright © 2023- Frello Technology Private Limited

import dotenv

dotenv.load_dotenv()

import os
import sys
import json
from fire import Fire
from typing import Optional

from chainfury import Chain
from chainfury.version import __version__
from chainfury.core import model_registry
from chainfury.types import Thread, Message


class CLI:
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
🌟 us on https://github.com/NimbleBoxAI/ChainFury
♥️  Built by [Tune AI](https://tunehq.ai) from ECR, Chennai 🌊
"""

    def run(
        self,
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

    def sh(
        self,
        api: str = "tuneapi",
        model: str = "rohan/mixtral-8x7b-inst-v0-1-32k",  # "kaushikaakash04/tune-blob"
        token: Optional[str] = None,
        stream: bool = True,
    ):
        cf_model = model_registry.get(api)
        if token is not None:
            cf_model.set_api_token(token)

        # loop for user input through command line
        thread = Thread()
        usr_cntr = 0
        while True:
            try:
                user_input = input(
                    f"\033[1m\033[33m  [{usr_cntr:02d}] YOU \033[39m:\033[0m "
                )
            except KeyboardInterrupt:
                break
            if user_input == "exit" or user_input == "quit" or user_input == "":
                break
            thread.add(Message(user_input, Message.HUMAN))

            print(f"\033[1m\033[34m ASSISTANT \033[39m:\033[0m ", end="", flush=True)
            if stream:
                response = ""
                for str_token in cf_model.stream_chat(thread, model=model):
                    response += str_token
                    print(str_token, end="", flush=True)
                print()  # new line
                thread.add(Message(response, Message.GPT))
            else:
                response = cf_model.chat(thread, model=model)
                print(response)

            thread.add(Message(response, Message.GPT))
            usr_cntr += 1


def main():
    Fire(CLI)

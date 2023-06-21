import os
import json
import fire
from pprint import pformat
from requests import Session
from typing import Dict, Any

from chainfury import (
    Chain,
    programatic_actions_registry,
    model_registry,
    Node,
    ai_actions_registry,
    Edge,
)

def _get_openai_token() -> str:
    openai_token = os.environ.get("OPENAI_TOKEN", "")
    if not openai_token:
        raise ValueError("OpenAI token not found")
    return openai_token


class _Nodes:
    def callp(self, fail: bool = False):
        """Call a programatic action"""
        node = programatic_actions_registry.get("call_api_requests")
        print("NODE:", node)
        data = {
            "method": "get",
            "url": "http://127.0.0.1:8000/api/v1/fury/components/",
            "headers": {"token": "my-booomerang-token"},
        }
        if fail:
            data["some-key"] = "some-value"
        out, err = node(data)
        if err:
            print("ERROR:", err)
            print("TRACE:", out)
            return
        print("OUT:", out)

    def callm(self, fail: bool = False):
        """Call a model"""
        model = model_registry.get("openai-completion")
        print("Found model:", model)
        data = {
            "openai_api_key": _get_openai_token(),
            "model": "text-curie-001",
            "prompt": "What comes after 0,1,1,2?",
        }
        if fail:
            data["model"] = "this-does-not-exist"
        out, err = model(data)
        if err:
            print("ERROR:", err)
            print("TRACE:", out)
            return
        print("OUT:", out)

    def callai(self, jtype: bool = False, fail: bool = False):
        """Call the AI action"""
        if fail:
            action_id = "write-a-poem"
        else:
            action_id = "hello-world"
            if jtype:
                action_id += "-2"
        action = ai_actions_registry.get(action_id)
        # print(action)

        out, err = action(
            {
                "openai_api_key": _get_openai_token(),
                "message": "hello world",
                "temperature": 0.12,
                # "style": "snoop dogg", # uncomment to get the fail version running correctly
            }
        )
        if err:
            print("ERROR:", err)
            print("TRACE:", out)
            return
        print("OUT:", out)

    def callai_chat(self, jtype: bool = False):
        """Call the AI action"""
        action_id = "chat-sum-numbers"
        if jtype:
            action_id += "-2"
        action = ai_actions_registry.get(action_id)
        print("ACTION:", action)

        out, err = action(
            {
                "openai_api_key": _get_openai_token(),
                "num1": "a mexican taco",
                "num2": "a spicy korean noodle",
            },
        )
        if err:
            print("ERROR:", err)
            print("TRACE:", out)
            return
        print("OUT:", out)


class _Chain:
    def callpp(self):
        p1 = programatic_actions_registry.get("call_api_requests")
        p2 = programatic_actions_registry.get("regex_substitute")
        e = Edge(p1.id, p2.id, ("text", "text"))
        c = Chain([p1, p2], [e])
        print("CHAIN:", c)

        # run the chain
        out, full_ir = c(
            {
                "method": "get",
                "url": "http://127.0.0.1:8000/api/v1/fury/components/",
                "headers": {"token": "booboo"},
                "pattern": "components",
                "repl": "booboo",
            }
        )
        print("BUFF:", pformat(full_ir))
        print("OUT:", pformat(out))

    def callpj(self, fail: bool = False):
        p = programatic_actions_registry.get("call_api_requests")

        # create a new ai action to build a poem
        NODE_ID = "sarcastic-agent"
        j = ai_actions_registry.register(
            node_id=NODE_ID,
            description="AI will add two numbers and give a sarscastic response. J-type action",
            model_id="openai-chat",
            model_params={
                "model": "gpt-3.5-turbo",
            },
            fn={
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello there, can you add these two numbers for me? 1023, 97. Be super witty in all responses.",
                    },
                    {
                        "role": "assistant",
                        "content": "It is 1110. WTF I mean I am a powerful AI, I have better things to do!",
                    },
                    {
                        "role": "user",
                        "content": "Can you explain this json to me? {{ json_thingy }}",
                    },
                ],
            },
            outputs={
                "chat_reply": ("choices", 0, "message", "content"),
            },
        )
        print("ACTION:", j)

        e = Edge(p.id, j.id, ("text", "json_thingy"))

        c = Chain(
            [p, j],
            [
                e,
            ],
        )
        print("CHAIN:", c)

        # run the chain
        out, full_ir = c(
            {
                "method": "get",
                "url": "http://127.0.0.1:8000/api/v1/components/",
                "headers": {"token": "booboo"},
                "openai_api_key": _get_openai_token(),
            }
        )
        print("BUFF:", pformat(full_ir))
        print("OUT:", pformat(out))

    def calljj(self):
        j1 = ai_actions_registry.get("hello-world")
        print("ACTION:", j1)
        j2 = ai_actions_registry.get("write-a-poem")
        print("ACTION:", j2)
        e = Edge(j1.id, j2.id, ("generation", "message"))
        c = Chain([j1, j2], [e])
        print("CHAIN:", c)

        # run the chain
        out, full_ir = c(
            {
                "openai_api_key": _get_openai_token(),
                "message": "hello world",
                "style": "snoop dogg",
            }
        )
        print("BUFF:", pformat(full_ir))
        print("OUT:", pformat(out))

    def callj3(self, quote: str, n: int = 4, thoughts: bool = False, to_json: bool = False):
        findQuote = ai_actions_registry.register(
            node_id="find-quote",
            model_id="openai-chat",
            model_params={
                "model": "gpt-3.5-turbo",
            },
            fn={
                "messages": [
                    {
                        "role": "user",
                        "content": "'{{ quote }}' \nWho said this quote, if you don't know then reply with a random character from history world? Give reply in less than 10 words.",
                    },
                ],
            },
            outputs={
                "chat_reply": ("choices", 0, "message", "content"),
            },
        )

        charStory = ai_actions_registry.register(
            node_id="tell-character-story",
            model_id="openai-chat",
            model_params={
                "model": "gpt-3.5-turbo",
            },
            fn={
                "messages": [
                    {"role": "user", "content": "Tell a small {{ story_size }} line story about '{{ character_name }}'"},
                ],
            },
            outputs={
                "characters_story": ("choices", 0, "message", "content"),
            },
        )
        rapMaker = ai_actions_registry.get("deep-rap-quote")
        e1 = Edge(findQuote.id, charStory.id, ("chat_reply", "character_name"))
        e2 = Edge(charStory.id, rapMaker.id, ("characters_story", "character"))
        c = Chain([findQuote, charStory, rapMaker], [e1, e2])
        print("CHAIN:", c)

        sample_input = {"openai_api_key": _get_openai_token(), "quote": quote, "story_size": n}  # these will also act like defaults
        # sample_input = {"quote": quote, "story_size": n}  # these will also act like defaults

        if to_json:
            print(json.dumps(c.to_dict("quote", f"{rapMaker.id}/chat_reply", sample_input), indent=2))
            return

        # run the chain
        sample_input["openai_api_key"] = _get_openai_token()
        out, full_ir = c(
            sample_input,
            print_thoughts=thoughts,
        )

        print("BUFF:", pformat(full_ir))
        print("OUT:", pformat(out))

    def from_json(self, quote: str = "", n: int = 4, mainline: bool = False, thoughts: bool = False, path: str = "./stories/fury.json"):
        with open(path) as f:
            dag = json.load(f)
        c = Chain.from_dict(dag)
        print("CHAIN:", c)

        if mainline:
            input = quote
        else:
            # run the chain
            input = {"openai_api_key": _get_openai_token()}
            if quote:
                input["quote"] = quote
            if n:
                input["story_size"] = n
        out, full_ir = c(
            input,
            print_thoughts=thoughts,
        )
        print("BUFF:", pformat(full_ir))
        print("OUT:", pformat(out))


if __name__ == "__main__":

    def help():
        return """
Fury Story
==========

python3 -m stories.fury nodes callp [--fail]
python3 -m stories.fury nodes callai [--jtype --fail]
python3 -m stories.fury nodes callai_chat [--jtype --fail]

python3 -m stories.fury chain callpp
python3 -m stories.fury chain callpj
python3 -m stories.fury chain calljj
python3 -m stories.fury chain callj3 --quote QUOTE
""".strip()

    fire.Fire({"nodes": _Nodes, "chain": _Chain, "help": help})

import os
import json
import fire
from requests import Session
from typing import Dict, Any

from fury import (
    Chain,
    programatic_actions_registry,
    model_registry,
    Node,
    ai_actions_registry,
)
import components  # import to register all the components that we have


def _get_openai_token() -> str:
    openai_token = os.environ.get("OPENAI_TOKEN", "")
    if not openai_token:
        raise ValueError("OpenAI token not found")
    return openai_token


class FormAiAction:
    # when the AI action is built using a form or via FE then we need to conver the JSON
    # configuration to a callable for the chain.
    def __init__(self, model_id: str, model_params: Dict[str, Any]):
        pass


class _Nodes:
    def callp(self, fail: bool = False):
        """Call a programatic action"""
        node = programatic_actions_registry.get("call_api_requests")
        print(node)

        data = {
            "method": "get",
            "url": "http://127.0.0.1:8000/api/v1/components/",
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

    def callai(self, fail: bool = False):
        """Call the AI action"""
        action = ai_actions_registry.get("hello-world")
        if fail:
            action = ai_actions_registry.get("write-a-poem")
        print(action)

        out, err = action(
            {
                "openai_api_key": _get_openai_token(),
                "message": "hello world",
                "temperature": 0.12,
            }
        )
        if err:
            print("ERROR:", err)
            print("TRACE:", out)
            return
        print("OUT:", out)

    def buildai(self):
        """Build an AI powered action"""
        nodes = Node.build_ai()

        model_data = {
            "model_id": "openai-completion",
            "model_params": {
                "openai_token": _get_openai_token(),
                "model": "text-curie-001",
                "prompt": "",
                "temperature": 0.1,
            },
            "prompt": {
                "type": "text",
                "text": "Answer a simple question about this JSON: `{{api_text}}` | Q: what is the key? | A: ",
            },
        }

        pass

    def call_chain(self, fail: bool = False):
        # this is an example to check if the entire enf to end chain is working correctly or not
        pass


if __name__ == "__main__":
    fire.Fire(
        {
            "nodes": _Nodes,
        }
    )

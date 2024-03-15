# Copyright © 2023- Frello Technology Private Limited

import unittest
from functools import cache
from chainfury.components.functional import echo
from chainfury import programatic_actions_registry, Chain, Var, Tools


class TestSerDeser(unittest.TestCase):
    """Tests Serialisation and Deserialisation of Nodes, Chains and Tools."""

    def test_chain_dict(self):
        Chain.from_dict(chain.to_dict())

    def test_chain_apidict(self):
        Chain.from_dict(chain.to_dict(api=True))

    def test_chain_json(self):
        Chain.from_json(chain.to_json())

    def test_chain_dag(self):
        Chain.from_dag(chain.to_dag())

    def test_node_dict(self):
        node = programatic_actions_registry.get("chainfury-echo")
        if node is None:
            self.fail("Node not found")
        self.assertIsNotNone(node)
        node.from_dict(node.to_dict())

    def test_node_json(self):
        node = programatic_actions_registry.get("chainfury-echo")
        if node is None:
            self.fail("Node not found")
        self.assertIsNotNone(node)
        node.from_json(node.to_json())

    def test_tool_dict(self):
        Tools.from_dict(tool.to_dict())

    def test_tool_json(self):
        Tools.from_json(tool.to_json())


class TestNode(unittest.TestCase):
    """Test Node specific functionality."""

    def test_node_run(self):
        node = programatic_actions_registry.get("chainfury-echo")
        if node is None:
            self.fail("Node not found")
        self.assertIsNotNone(node)
        out, err = node(data={"message": "hi there"})
        self.assertIsNone(err)

        # call the function directly
        fn_out, _ = echo("hi there")
        self.assertEqual(out, {"message": fn_out})


#
# Chain definition
#

chain = Chain(
    name="echo-cf-public",
    description="abyss",
    nodes=[programatic_actions_registry.get("chainfury-echo")],  # type: ignore
    sample={"message": "hi there"},
    main_in="message",
    main_out="chainfury-echo/message",
)


#
# Tool definition
#
tool = Tools(
    name="calculator",
    description=(
        "This tool is a calculator, it can perform basica calculations. "
        "Use this when you are trying to do some mathematical task"
    ),
)


@tool.add(
    description="This function adds two numbers",
    properties={
        "a": Var("int", required=True, description="number one"),
        "b": Var("int", description="number two"),
    },
)
def add_two_numbers(a: int, b: int = 10):
    return a + b


@tool.add(
    description="This calculates square root of a number",
    properties={
        "a": Var("int", description="number to calculate square root of"),
    },
)
def square_root_number(a):
    import math

    return math.sqrt(a)


if __name__ == "__main__":
    unittest.main()

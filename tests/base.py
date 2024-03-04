# Copyright © 2023- Frello Technology Private Limited

from chainfury import programatic_actions_registry, Chain
from chainfury.components.functional import echo

import unittest


chain = Chain(
    name="echo-cf-public",
    description="abyss",
    nodes=[programatic_actions_registry.get("chainfury-echo")],  # type: ignore
    sample={"message": "hi there"},
    main_in="message",
    main_out="chainfury-echo/message",
)


class TestSerDeser(unittest.TestCase):
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


class TestNode(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

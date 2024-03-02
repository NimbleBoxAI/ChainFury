# Copyright © 2023- Frello Technology Private Limited

from chainfury import programatic_actions_registry, Chain

import unittest


chain = Chain(
    name="echo-cf-public",
    description="abyss",
    nodes=[programatic_actions_registry.get("chainfury-echo")],  # type: ignore
    sample={"message": "hi there"},
    main_in="message",
    main_out="chainfury-echo/message",
)


class TestChainSerDeser(unittest.TestCase):
    def test_dict(self):
        Chain.from_dict(chain.to_dict())

    def test_apidict(self):
        Chain.from_dict(chain.to_dict(api=True))

    def test_json(self):
        Chain.from_json(chain.to_json())

    def test_dag(self):
        Chain.from_dag(chain.to_dag())


if __name__ == "__main__":
    unittest.main()

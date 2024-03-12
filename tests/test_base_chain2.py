# Copyright © 2023- Frello Technology Private Limited

from chainfury import (
    Chain,
    Thread,
    human,
)
from chainfury.components.tune import TuneModel
import unittest


chain = Chain(
    name="demo-one",
    description=(
        "Building the hardcore example of chain at https://nimbleboxai.github.io/ChainFury/examples/usage-hardcore.html "
        "using threaded chains"
    ),
    main_in="stupid_question",
    main_out="fight_scene/fight_scene",
    default_model=TuneModel("rohan/mixtral-8x7b-inst-v0-1-32k"),
)
chain.add_thread(
    "character_one",
    Thread(
        human(
            "You were who was running in the middle of desert. You see a McDonald's and the waiter ask a stupid "
            "question like: '{{ stupid_question }}'? You are pissed and you say."
        ),
    ),
)
chain.add_thread(
    "character_two",
    Thread(
        human(
            "Someone comes upto you in a bar and screams '{{ character_one }}'? You are a bartender give a funny response to it."
        ),
    ),
)
chain.add_thread(
    "fight_scene",
    Thread(
        human(
            "Two men were fighting in a bar. One yelled '{{ character_one }}'. Other responded by yelling '{{ character_two }}'.\n"
            "Continue this story for 3 more lines."
        )
    ),
)


class TestChain(unittest.TestCase):
    """Testing Chain specific functionality"""

    def test_chain_toposort(self):
        self.assertEqual(
            chain.topo_order,
            ["character_one", "character_two", "fight_scene"],
        )


if __name__ == "__main__":
    unittest.main()

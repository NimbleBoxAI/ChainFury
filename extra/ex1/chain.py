# Copyright © 2023- Frello Technology Private Limited

from fire import Fire

from chainfury.base import Chain
from chainfury.chat import human, Message, Chat

from chainfury.components.openai import OpenaiGPTModel
from chainfury.components.tune import TuneModel


def main(q: str, openai: bool = False):
    chain = Chain(
        name="demo-one",
        description=(
            "Building the hardcore example of chain at https://nimbleboxai.github.io/ChainFury/examples/usage-hardcore.html "
            "using threaded chains"
        ),
        main_in="stupid_question",
        main_out="fight_scene/fight_scene",
        default_model=(
            OpenaiGPTModel("gpt-3.5-turbo")
            if openai
            else TuneModel("rohan/mixtral-8x7b-inst-v0-1-32k")
        ),
    )
    print("before:")
    print(chain)

    chain = chain.add_thread(
        "character_one",
        Chat(
            [
                human(
                    "You were who was running in the middle of desert. You see a McDonald's and the waiter ask a stupid "
                    "question like: '{{ stupid_question }}'? You are pissed and you say."
                )
            ]
        ),
    )

    chain = chain.add_thread(
        "character_two",
        Chat(
            [
                human(
                    "Someone comes upto you in a bar and screams '{{ character_one }}'? You are a bartender give a funny response to it."
                )
            ]
        ),
    )

    chain = chain.add_thread(
        "fight_scene",
        Chat(
            [
                human(
                    "Two men were fighting in a bar. One yelled '{{ character_one }}'. Other responded by yelling '{{ character_two }}'.\n"
                    "Continue this story for 3 more lines."
                )
            ]
        ),
    )

    print("---------------")
    print(chain)

    print(chain.topo_order)
    for ir, done in chain.stream(q):
        # print(ir)
        pass

    print("---------------")
    print(ir)


if __name__ == "__main__":
    Fire(main)

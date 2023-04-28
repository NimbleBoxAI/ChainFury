from typing import Any, List


class Model:
    # user can subclass this and override the __call__
    def __call__(self, *args, **kwargs):
        ...


class Memory:
    # user can subclass this and override the following functions
    def get(self, key: str):
        ...

    def put(self, key: str, value: Any):
        ...


class Chain:
    def __init__(self, agent: "Agent"):
        # so the chain can access all the underlying elements of Agent including:
        # - models
        # - memories
        self.agent = Agent

    # user can subclass this and override the __call__
    def __call__(self):
        ...


# the main class, user can either subclass this or prvide the chain
class Agent:
    def __init__(self, models: List[Model], memories: List[Memory], chain: Chain):
        self.models = models
        self.memories = memories
        self.chain = chain

    def __call__(self, user_input: Any):
        return self.chain(user_input)


if __name__ == "__main__":
    pass

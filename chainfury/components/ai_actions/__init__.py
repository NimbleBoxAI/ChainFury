from chainfury import ai_actions_registry, Model


# this is a super generic function to reply funnily to something
def hello_world(message: str):
    return {
        "prompt": f"Give a witty response for this: 'Hello dear AI agent, {message}'\n\nWitty Response:",
    }


ai_actions_registry.register(
    node_id="hello-world",
    description="Python function loaded from a file used as an AI action",
    model_id="openai-completion",
    model_params={
        "model": "text-curie-001",
        "temperature": 0.1,
    },
    fn=hello_world,
    outputs={
        "generations": ("choices", 0, "text"),
    },
)


ai_actions_registry.register(
    node_id="deep-rap-quote",
    description="J-type action will write a deep poem in the style of a character",
    model_id="openai-chat",
    model_params={
        "model": "gpt-3.5-turbo",
    },
    fn={
        "messages": [
            {
                "role": "user",
                "content": "give a deep 8 line rap quote on life in the style of {{ character }}.",
            },
        ],
    },
    outputs={
        "chat_reply": ("choices", 0, "message", "content"),
    },
)

from fury import ai_actions_registry, Model


# this is a super generic function to reply funnily to something
def hello_world(message: str, model: Model):
    prompt = f"Give a witty response for this: 'Hello dear AI agent, {message}'\n\nWitty Response:"
    options = model(
        {
            "prompt": prompt,
        }
    )
    return options


ai_actions_registry.register(
    node_id="hello-world",
    description="AI will respond with a hello world.",
    model_id="openai-completion",
    model_params={
        "model": "text-curie-001",
        "temperature": 0.1,
    },
    fn=hello_world,
)


# a generic function to write a poem from the given message
def write_a_poem(message: str, model: Model):
    prompt = f"Write a poem for this: '{message}'\n\nPoem:"
    options = model(
        {
            "prompt": prompt,
        }
    )
    return options


ai_actions_registry.register(
    node_id="write-a-poem",
    description="AI will write a poem.",
    model_id="openai-completion",
    model_params={
        "model": "text-curie-001",
        "temperature": 0.1,
    },
    fn=write_a_poem,
)

from fury import ai_actions_registry, Model


# this is a super generic function to reply funnily to something
def hello_world(message: str):
    return {
        "prompt": f"Give a witty response for this: 'Hello dear AI agent, {message}'\n\nWitty Response:",
    }


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

ai_actions_registry.register(
    node_id="hello-world-2",
    description="J-type action that uses jinja templating instead of pre-loaded python functions",
    model_id="openai-completion",
    model_params={
        "model": "text-curie-001",
        "temperature": 0.1,
    },
    fn={
        "prompt": 'Give a witty response for this: "Hello dear AI agent, {{ message }}"\n\nWitty Response:',
    },
)


# a generic function to write a poem from the given message
def write_a_poem(message: str, style: str):
    options = {
        "prompt": f"Write a poem for this: '{message}' in the style of {style}\n\nPoem:",
        "max_tokens": 1024,
    }
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

ai_actions_registry.register(
    node_id="write-a-poem-2",
    description="J-type action that uses jinja templating instead of pre-loaded python functions",
    model_id="openai-completion",
    model_params={
        "model": "text-curie-001",
        "temperature": 0.1,
    },
    fn={
        "prompt": 'Write a poem for this: "{{ message }}" in the style of {{ style }}\n\nPoem:',
        "max_tokens": 1024,
    },
)


# a generic function that talks to the chatGPT model
def sum_of_two_numbers(num1: str, num2: str):
    return {
        "messages": [
            {
                "role": "system",
                "content": "You are a sarcastic but helful chatbot trying to answer questions that the user has",
            },
            {
                "role": "user",
                "content": "Hello there, can you add these two numbers for me? 123, 456",
            },
            {
                "role": "assistant",
                "content": "Sure I can help with that, as if I don't have anything better to do",
            },
            {
                "role": "user",
                "content": f"Can you add these two numbers for me? {num1}, {num2}",
            },
        ]
    }


ai_actions_registry.register(
    node_id="chat-sum-numbers",
    description="AI will add two numbers and give a sarscastic response.",
    model_id="openai-chat",
    model_params={
        "model": "gpt-3.5-turbo",
    },
    fn=sum_of_two_numbers,
)

ai_actions_registry.register(
    node_id="chat-sum-numbers-2",
    description="AI will add two numbers and give a sarscastic response. J-type action",
    model_id="openai-chat",
    model_params={
        "model": "gpt-3.5-turbo",
    },
    fn={
        "messages": [
            {
                "role": "system",
                "content": "You are a sarcastic but helful chatbot trying to answer questions that the user has",
            },
            {
                "role": "user",
                "content": "Hello there, can you add these two numbers for me? 1023, 97",
            },
            {
                "role": "assistant",
                "content": "It is 1110, as if I don't have anything better to do",
            },
            {
                "role": "user",
                "content": "Can you add these two numbers for me? {{ num1 }}, {{ num2 }}",
            },
        ],
    },
)

from chainfury import ai_actions_registry, Model


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
    outputs={"generation": ("choices", 0, "text")},
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
    outputs={"generations": ("choices", 0, "text")},
)


# a generic function to write a poem from the given message
ai_actions_registry.register(
    node_id="write-a-poem",
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
    outputs={"generations": ("choices", 0, "text")},
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
    outputs={"chat_reply": ("choices", 0, "message", "content")},
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
    outputs={"chat_reply": ("choices", 0, "message", "content")},
)

ai_actions_registry.register(
    node_id="deep-rap-quote",
    description="AI will tell a joke on any topic you tell it to talk about",
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
    outputs={"chat_reply": ("choices", 0, "message", "content")},
)

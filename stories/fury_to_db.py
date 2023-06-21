from chainfury import ai_actions_registry

sensational_story = ai_actions_registry.register(
    node_id="sensation-story",
    model_id="openai-chat",
    model_params={
        "model": "gpt-3.5-turbo",
    },
    fn={
        "messages": [
            {
                "role": "user",
                "content": "You are a Los Santos correspondent and saw '{{ scene }}'. Make it into a small 6 line witty, sarcastic, funny sensational story as if you are on Radio Mirror Park.",
            },
        ],
    },
    outputs={
        "story": ("choices", 0, "message", "content"),
    },
)

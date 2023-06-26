# from chainfury import ai_actions_registry, cf_client

# make an action
sensational_story = ai_actions_registry.to_action(
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

#
# sensational_story = cf_client.get_or_create_node(sensational_story)
out = sensational_story("there are times, when I don't know what to do!")

# what are some interesting algorithms that we can build using fury?

import re
import fire
from pprint import pformat

from chainfury import Chain, ai_actions_registry, Edge


class Actions:
    topic_to_synopsis = ai_actions_registry.to_action(
        action_name="topic-to-synopsis",
        model_id="openai-chat",
        model_params={
            "model": "gpt-3.5-turbo",
        },
        fn={
            "messages": [
                {
                    "role": "user",
                    "content": "You are a funny GTA game agent give a one-liner of a wild story around the following topics.\n\ntopics: UFO, burger king",
                },
                {
                    "role": "assistant",
                    "content": "The UFOs drop by Burger King, like the smell of it",
                },
                {
                    "role": "user",
                    "content": "You are a funny GTA game agent give a one-liner of a wild story around the following topics.\n\ntopics: Car, white socks",
                },
                {
                    "role": "assistant",
                    "content": "Car robbed by an army of white socks",
                },
                {
                    "role": "user",
                    "content": "You are a funny GTA game agent give a one-liner of a wild story around the following topics.\n\ntopics: {{ topics }}",
                },
            ],
        },
        outputs={
            "synopsis": ("choices", 0, "message", "content"),
        },
    )

    sensational_story = ai_actions_registry.to_action(
        action_name="sensation-story",
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

    sensational_story_nbx = ai_actions_registry.to_action(
        action_name="sensation-story-nbx",
        model_id="nbx-deploy",
        model_params={
            "max_new_tokens": 256,
        },
        fn={
            "inputs": "User: You are a Los Santos correspondent and saw '{{ scene }}'. Make it into a small 6 line witty, sarcastic, funny sensational story as if you are on Radio Mirror Park.\n\nAssistant: ",
        },
        outputs={
            "story": ("generated_text",),
        },
    )

    sensational_story_generator = ai_actions_registry.to_action(
        action_name="story-multi-generator",
        model_id="openai-completion",
        model_params={
            "model": "text-babbage-001",
            "max_tokens": 128,
        },
        fn={
            "prompt": """Complete the following Story

headline: {{ headline }}

sub-headline: {{ sub_headline }}

64 word story:""",
        },
        outputs={"story": ["choices", 0, "text"]},
    )

    catchy_headline = ai_actions_registry.to_action(
        action_name="catchy-headline",
        model_id="openai-chat",
        model_params={
            "model": "gpt-3.5-turbo",
        },
        fn={
            "messages": [
                {
                    "role": "user",
                    "content": "Convert this news story into a funny headline with less than 6 words:\n\n{{ story }}",
                },
            ],
        },
        outputs={
            "headline": ("choices", 0, "message", "content"),
        },
    )

    corrupt_editor_check = ai_actions_registry.to_action(
        action_name="passes-editor",
        model_id="openai-chat",
        model_params={
            "model": "gpt-3.5-turbo",
        },
        fn={
            "messages": [
                {
                    "role": "user",
                    "content": """"In the wild streets of Los Santos, chaos reigned supreme as the Fred,
a gutsy yet unfortunate bloke, sprinted through the concrete jungle. With the speed of a stolen Banshee, he
raced towards an unexpected collision course. Alas! Fate's cruel hand guided him straight into the sturdy
arms of a towering oak, leaving his pride scattered like collectible spaceship parts. Amidst the laughter of
onlookers and the sarcastic honking of passing cars, our hero learned a valuable lesson: in this city of mayhem,
even the trees had a grudge against him."

In this story is there a mention of any ['Franklin', 'Trevor', 'Micheal'] from the game:
- if mentioned reply with "story-reject"
- else reply with "story-accept"
""",
                },
                {
                    "role": "assistant",
                    "content": '"story-accept"',
                },
                {
                    "role": "user",
                    "content": '"{{ story }}"\nIn this story is there a mention of any protagonist from the game:'
                    '\n- if protagonist mentioned reply with "story-reject"'
                    '\n- else reply with "story-accept"',
                },
            ],
        },
        outputs={
            "story_accepted": ("choices", 0, "message", "content"),
        },
    )

    people_feedback = ai_actions_registry.to_action(
        action_name="people-feedback",
        model_id="openai-chat",
        model_params={
            "model": "gpt-3.5-turbo",
        },
        fn={
            "messages": [
                {
                    "role": "user",
                    "content": "On the scale of 0 (plausible) - 10 (ridiculously funny), how wild is this story? Reply format:\n\n```\nrating: xxxxx\nreason: xxxx\n```\n\n{{ story }}",
                },
            ],
        },
        outputs={
            "story_accepted": ("choices", 0, "message", "content"),
        },
    )


class Chains:
    story = Chain(
        [Actions.sensational_story],
        sample={"scene": ""},
        main_in="scene",
        main_out=f"{Actions.sensational_story.id}/story",
    )  # type: ignore

    story_nbx = Chain(
        [Actions.sensational_story_nbx],
        sample={"scene": ""},
        main_in="scene",
        main_out=f"{Actions.sensational_story_nbx.id}/story",
    )  # type: ignore

    feedback = Chain(
        [Actions.people_feedback],
        sample={"story": ""},
        main_in="story",
        main_out=f"{Actions.people_feedback.id}/story_accepted",
    )  # type: ignore

    news = Chain(
        [Actions.sensational_story, Actions.catchy_headline],
        [
            Edge(Actions.sensational_story.id, "story", Actions.catchy_headline.id, "story"),
        ],
        sample={"scene": ""},
        main_in="scene",
        main_out=f"{Actions.catchy_headline.id}/headline",
    )

    topic_to_story = Chain(
        [Actions.topic_to_synopsis, Actions.sensational_story, Actions.catchy_headline],
        [
            Edge(Actions.topic_to_synopsis.id, "synopsis", Actions.sensational_story.id, "scene"),
            Edge(Actions.sensational_story.id, "story", Actions.catchy_headline.id, "story"),
        ],
        sample={"topics": ""},
        main_in="topics",
        main_out=f"{Actions.catchy_headline.id}/headline",
    )

    more_variants = Chain(
        [
            Actions.topic_to_synopsis,
            Actions.sensational_story,
            Actions.catchy_headline,
            Actions.sensational_story_generator,
        ],
        [
            Edge(Actions.topic_to_synopsis.id, "synopsis", Actions.sensational_story.id, "scene"),
            Edge(Actions.sensational_story.id, "story", Actions.catchy_headline.id, "story"),
            Edge(Actions.catchy_headline.id, "headline", Actions.sensational_story_generator.id, "headline"),
            Edge(Actions.topic_to_synopsis.id, "synopsis", Actions.sensational_story_generator.id, "sub_headline"),
        ],
        sample={"topics": ""},
        main_in="topics",
        main_out=f"{Actions.catchy_headline.id}/headline",
    )

    good_story = Chain(
        [Actions.sensational_story, Actions.corrupt_editor_check],
        [Edge(Actions.sensational_story.id, "story", Actions.corrupt_editor_check.id, "story")],  # type: ignore
        sample={"scene": ""},
        main_in="scene",
        main_out=f"{Actions.corrupt_editor_check.id}/story_accepted",
    )  # type: ignore


# input/output prompting
def io_prompting(scene: str, v: bool = False):
    out, thoughts = Chains.story(scene)  # type: ignore
    if v:
        print("BUFF:", pformat(thoughts))
        print(" OUT:", out)
    return out


# chain of thought prompting (CoT)
# https://arxiv.org/pdf/2201.11903.pdf
def chain_of_thought(scene: str, v: bool = False):
    out, thoughts = Chains.news(scene)  # type: ignore
    if v:
        print("BUFF:", pformat(thoughts))
        print(" OUT:", out)
    return out


# self consistency with CoT (CoT-SC)
# https://arxiv.org/pdf/2203.11171.pdf
def cot_consistency(scene, n: int = 3, v: bool = False, pb: bool = False):
    out = dict()
    full_buffer = []
    for i in range(n):
        final_answer, thoughts = Chains.good_story(scene)  # type: ignore
        if pb:
            print(f"[sample #{i:02d}] BUFF:", pformat(thoughts))
        print(f"[sample #{i:02d}]  OUT:", final_answer)
        out.setdefault(final_answer, 0)
        out[final_answer] += 1
        full_buffer.append(thoughts)
    if v:
        print("COUNTS:", pformat(out))
        print("Final answer:", max(out, key=out.get))  # type: ignore

    return out


# tree of thought (ToT): https://arxiv.org/pdf/2305.10601.pdf
# this is slightly more complex as it needs to incorporate a value function and a step function
# see how you can use fury as a library to build this
class TreeOfThought:
    def __init__(self, max_search_space: int = 5):
        # if bfs:
        #     print("Order: Breadth (BFS)")
        # else:
        #     print("Order: Depth (DFS)")

        self.max_search_space = max_search_space
        self.step_fn = Chains.topic_to_story
        self.value_fn = Chains.feedback

    def __call__(self, topics: str, v: bool = False):
        done = False
        total_searches = 0
        result = None
        max_rating = -1
        while not done:
            # call each node
            out, thoughts = Chains.topic_to_story(topics)  # type: ignore
            if v:
                print("BUFF:", pformat(thoughts))
                print(" OUT:", out)

            # get feedback for the node
            feedback, _ = Chains.feedback(thoughts[f"{Actions.sensational_story.id}/story"]["value"])  # type: ignore
            if v:
                print("FDBK:", feedback)

            # quanify the feedback
            out = re.findall(r"rating: ([0-9]+)", feedback)  # type: ignore
            if not out:
                rating = 0
            else:
                rating = int(out[0])
            print("RATING:", rating)

            # just tree-search things
            total_searches += 1
            if max_rating < rating:
                result = (out, thoughts, feedback)
                max_rating = rating
            if total_searches >= self.max_search_space:
                done = True
        return max_rating, result


def tree_of_thought(topics: str, max_search_space: int = 5, v: bool = False):
    # write a the funniest story you can think of based on the keywords given by the user
    # funniest metric: rating that we get from the feedback
    if isinstance(topics, tuple):
        topics = ", ".join(topics)
    tot = TreeOfThought(max_search_space=max_search_space)
    max_rating, result = tot(topics, v=v)
    return max_rating, result


if __name__ == "__main__":
    # print(Chains.topic_to_story.to_json())
    fire.Fire(
        {
            "algo": {
                "io": io_prompting,
                "cot": chain_of_thought,
                "cot-sc": cot_consistency,
                "tot": tree_of_thought,
            },
        }
    )

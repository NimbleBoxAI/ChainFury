# ChainFury components

This folder contains code for all the different kinds of components that can be used inside your agents. These aim here is to be a demonstrator and show people how they can go ahead and build their own things.

## Functional

[functional](./functional/) contains all the functions that are wrapped to make the programatic actions (`p-nodes`).

## Models

We have added [openai](./openai/) and [stability](./stability/) as providers for the machine intelligence. We have called these APIs directly instead of using packages to keep things as open as possible.

## AI Agents

As mentioned in [our blog](https://gist.github.com/yashbonde/885ef52dd69b44c46b4655a116d25d4c) AI actions are powered using models. Each AI action has an associated `model` which processes the inputs provided. There are two different ways to build AI actions.
- One strategy is to provide preprocessing function that takes in a bunch of JSON-serialisable arguments and returns a dictionary that is eventually passed to the underlying model.
- In another strategy we can build the preprocessing function completely using a JSON based message. The prompting engine can be `jinja2`

The folder [ai_actions](./ai_actions/) contains code for both of them. Actually the former is a really bad strategy because it hides from the user what are the things that the black box is going to do, which is against the idea of being open. However ther are several complex things that cannot be done with just jinja, ex. chat APIs which require an array of chat objects.

## Challenges

We would like to enforce a certain kind of interface pattern for all the actions. All functions should return `(data, err)` tuple.

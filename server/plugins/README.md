# Plugins

ChainFury should be as interactble as people want. It is important that it be done correctly, so here's how we want to do it.

## Architecture

When we say "Plugin" we are talking about the user built plugins and "Plugin Handler" is the object created by each worker that handles connections to all these plugins.

- Avoid imports from outside this module to inside this module

## How to start?

Open `[echo](./echo/__init__.py)` plugin to see how you can build your own.


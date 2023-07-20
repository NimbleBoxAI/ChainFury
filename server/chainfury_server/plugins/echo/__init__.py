from chainfury_server.plugins.base import CFPluginMetadata, CFPlugin, Event


class EchoPlugin(CFPlugin):
    def handle(self, event: Event):
        if event.event_type == Event.types.PROCESS_PROMPT:
            """
            Process prompt is called when the user has requested a prompt completion and the bot has generated
            the response. This means you will have access to the entire chain of thought as well as the DB Row.
            """
            from chainfury_server.commons.langflow_utils import CFPromptResult

            result: CFPromptResult = event.data
            print("          result:", result.result)
            print("number of tokens:", result.num_tokens)
            print("      # thoughts:", len(result.thought))


# Creators will have to define an instance of CFPluginMetadata with name 'plugin_meta' fixed because this is
# what the loader is configured to look for, no there are no changes to this. FAQ:
# - versioning will be handled by creating a new plugin
plugin_meta = CFPluginMetadata(
    name="echo",
    version="0.1",
    plugin_class=EchoPlugin,
)

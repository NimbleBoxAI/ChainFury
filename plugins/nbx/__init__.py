from server.commons.plugins.base import PluginBase, Event, PluginHandler


class GraphanaPlugin(PluginBase):
    name: str = "graphana-v1"
    import_name: str = "plugins.graphana"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graphana_logger = GraphanaLogger()

    def _parse_to_grphan(self, event: Event) -> str:
        # do something with the event
        return "graphana string"

    def handle_event(self, event: Event, handler: PluginManager):
        # do something with the event
        if event.type == "something-useful":
            self.graphana_logger.log(self._parse_to_grphan(event))

        # or make a change the server via plugin handler
        action = some_function(event)
        if action == "disable_key":
            handler.disable_key(action.data)

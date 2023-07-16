from chainfury_server.plugins import CFPlugin, Event

from nbox.lmao_v4.project import Project_v4


# lol even though this is valid in python this is invalid in golang
def convert_string_to_uuid(x: int):
    # 8-4-4-4-12 =
    if len(str(x)) > 32:
        raise ValueError("UUIDs are 36 characters long")
    print("making uuid from:", x)
    _x = f"{x:032d}"
    not_uuid = _x[:8] + "-" + _x[8:12] + "-" + _x[12:16] + "-" + _x[16:20] + "-" + _x[20:]
    print("making uuid from:", not_uuid)
    try:
        from uuid import UUID

        UUID(not_uuid, version=4)
    except ValueError:
        raise ValueError("Invalid UUID")
    return not_uuid


class NimbleBoxPlugin(CFPlugin):
    def __init__(self, project_id: str):
        super().__init__()
        self.pid = project_id
        self.project = Project_v4(self.pid)
        self.tracker = self.project.get_live_tracker(
            metadata={
                "name": "NimbleBox ChainFury Plugin",
                "version": "0.0.1",
            }
        )

    def handle(self, event: Event):
        if event.event_type == Event.types.PROCESS_PROMPT:
            """
            Process prompt is called when the user has requested a prompt completion and the bot has generated
            the response. This means you will have access to the entire chain of thought as well as the DB Row.
            """
            from chainfury_server.commons.langflow_utils import CFPromptResult

            result: CFPromptResult = event.data
            self.tracker.log(
                {
                    "event_type": event.event_type,
                    "result": result.result,
                    "num_tokens": result.num_tokens,
                    "prompt_id": result.prompt.id,  # type: ignore
                    "chatbot_id": result.prompt.chatbot_id,  # type: ignore
                },
            )

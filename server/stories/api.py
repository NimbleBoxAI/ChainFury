import os
import fire
import json
from uuid import uuid4
from requests import Session


def hr(msg: str = ""):
    width = os.get_terminal_size().columns
    if len(msg) > width - 5:
        print("=" * width)
        print(msg)
        print("=" * width // 2)  # type: ignore
    else:
        print("=" * (width - len(msg) - 1) + " " + msg)


TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluLTIiLCJ1c2VyaWQiOiJuZzU0d3l4YSJ9.fs7Ejjx9sRYG9LIVU7VHZm5CSzK8HIK0hUyL0k5iirk"
URL = "http://127.0.0.1:8000/api/v1"

sess = Session()
sess.headers.update({"token": TOKEN})


class AuthAPI:
    def signup(self, username: str, password: str = "admin", email: str = "foo@bar.com", v: bool = False):
        r = sess.post(
            f"{URL}/signup",
            json={
                "username": username,
                "password": password,
                "email": email,
            },
        )
        out = r.json()
        if v:
            print(json.dumps(out, indent=2))
        return out

    def login(self, username, password: str = "admin", v: bool = False):
        r = sess.post(f"{URL}/login", json={"username": username, "password": password})
        out = r.json()
        if v:
            print(json.dumps(out, indent=2))
        return out


class ChatbotAPI:
    def init(self, name: str, v: bool = False):
        out = sess.post(f"{URL}/chatbot/", json={"name": name, "engine": "fury"})
        if v:
            print(out.json())
        return out.json()

    def show(self, id: str, v: bool = False):
        out = sess.get(f"{URL}/chatbot/{id}")
        if v:
            print(out.json())
        return out.json()

    def update(self, id: str, name: str, dag: bool = False, v: bool = False):
        update_req = {"name": name, "update_keys": ["name"]}
        if dag:
            update_req["dag"] = {
                "nodes": [
                    {"id": "unq-1", "position": {"x": 0, "y": 0}, "type": "FuryEngineNode", "width": 128, "height": 128},
                    {"id": "unq-2", "position": {"x": 0, "y": 0}, "type": "FuryEngineNode", "width": 128, "height": 128},
                ],
                "edges": [
                    {"source": "unq-1", "sourceHandle": "t", "target": "unq-2", "targetHandle": "o", "id": "<IDK>"},
                ],
            }
            update_req["update_keys"].append("dag")

        out = sess.put(f"{URL}/chatbot/{id}", json=update_req)
        if v:
            print(out.json())
        return out.json()

    def delete(self, id: str, v: bool = False):
        out = sess.delete(f"{URL}/chatbot/{id}")
        if v:
            print(out.json())
        return out.json()

    def list(self, v: bool = False):
        out = sess.get(f"{URL}/chatbot/")
        if v:
            print(out.json())
        return out.json()

    def story(self, name: str):
        # fmt: off
        hr("Create chatbot"); out = self.init(name); print("New chatbot:", out)
        hr("List chatbots"); chatbots = self.list()["chatbots"]; print("total chatbots:", len(chatbots))
        hr("Show chatbot"); out = self.show(out["id"]); print("chatbot:", out)
        hr("Update chatbot"); out = self.update(out["id"], name="new name"); print("updated chatbot:", out)
        hr("Delete chatbot"); out = self.delete(out["id"]); print("deleted chatbot:", out)
        hr("List chatbots"); out = self.list(); print("total chatbots:", len(out))
        # fmt: on


class FuryAPI:
    # components API
    def comp(self, v: bool = False):
        out = sess.get(f"{URL}/fury/")
        if v:
            print(out.json())
        return out.json()

    def list_comp(self, id: str, v: bool = False):
        out = sess.get(f"{URL}/fury/components/{id}")
        if v:
            print(out.json())
        return out.json()

    def get_comp(self, id: str, cid: str, v: bool = False):
        out = sess.get(f"{URL}/fury/components/{id}/{cid}")
        if v:
            print(out.json())
        return out.json()

    # fury actions API
    def create(self, name: str = "Catchy headline", description: str = "created by stories file", bad: bool = False, v: bool = False):
        action_req = {
            "name": name,
            "description": description,
            "fn": {
                "model_id": "openai-chat",  # taken from the /components/models API
                "model_params": {
                    "model": "gpt-3.5-turbo"
                },  # this value is again a JSON that can be hardcoded by the FE while we figure out the API
                # this JSON is put into the API as is, taken from the text box
                "fn": {
                    "messages": [
                        {"role": "user", "content": "Convert this news story into a funny headline with less than 6 words:\n\n{{ story }}"}
                    ]
                },
            },
            # for now FE can hardcode the type and loc for developer convinience, this cannot be sent by the backend
            # I'll need to provide Vikrant with a list of these values
            "outputs": [{"type": "string", "name": "headline", "loc": ["choices", 0, "message", "content"]}],
        }
        if bad:
            del action_req["fn"]["model_id"]
        r = sess.post(f"{URL}/fury/actions/", json=action_req)
        try:
            r.raise_for_status()
        except Exception as e:
            print(f"ERROR\t{r.status_code}\t{r.text}")

        out = r.json()
        if v:
            print(json.dumps(out, indent=2))
        return out

    def show(self, id: str, v: bool = False):
        r = sess.get(f"{URL}/fury/actions/{id}")
        out = r.json()
        if v:
            print(json.dumps(out, indent=2))
        return out

    def update(
        self, id: str, name: str, fn: bool = False, bad: bool = False, description: str = "Description now changed", v: bool = False
    ):
        action_update_req = {"name": name, "description": description, "update_fields": ["name", "description"]}
        if fn:
            action_update_req["fn"] = {
                "model_id": "openai-chat",  # taken from the /components/models API
                "model_params": {
                    "model": "gpt-3.5-turbo"
                },  # this value is again a JSON that can be hardcoded by the FE while we figure out the API
                # this JSON is put into the API as is, taken from the text box
                "fn": {
                    "messages": [
                        {
                            "role": "user",
                            "content": "Convert this news story into a funny headline with less than 6 words:\n\n{{ story }}",
                        }
                    ]
                },
            }
            action_update_req["update_fields"].append("fn")

            # for now FE can hardcode the type and loc for developer convinience, this cannot be sent by the backend
            # I'll need to provide Vikrant with a list of these values
            action_update_req["outputs"] = [{"type": "string", "name": "headline", "loc": ["choices", 0, "message", "content"]}]
            if bad:
                del action_update_req["outputs"]

        r = sess.put(f"{URL}/fury/actions/{id}", json=action_update_req)
        out = r.json()
        if v:
            print(json.dumps(out, indent=2))
        return out

    def delete(self, id: str, v: bool = False):
        r = sess.delete(f"{URL}/fury/actions/{id}")
        out = r.json()
        if v:
            print(json.dumps(out, indent=2))
        return out

    def list(self, offset=0, limit=25, v: bool = False):
        r = sess.get(
            f"{URL}/fury/actions/",
            params={"offset": offset, "limit": limit},
        )
        out = r.json()
        if v:
            print(json.dumps(out, indent=2))
        return out

    def story(self, name: str = "foobar", fn: bool = False):
        # fmt: off

        # the components APIs are just to be called
        hr("Components API"); comps = self.comp(); print(comps)
        for k in comps["components"]:
            hr(f"List '{k}'"); out = self.list_comp(k); print(len(out))
            hr(f"Get '{k}'"); out = self.get_comp(k, out[next(iter(out))]["id"]); print(out)

        # test
        hr("Create Action"); out = self.create(); print(out)
        hr("List Action"); actions_list = self.list(); print(len(actions_list))
        hr("Show Action"); out = self.show(out["id"]); print(out)
        hr("Update Action"); out = self.update(out["id"], name=name, fn=fn); print(out)
        hr("Delete Action"); delete_message = self.delete(out["id"]); print(delete_message)
        hr("List Actions"); actions_list = self.list(); print(len(actions_list))
        # fmt: on


class PromptsAPI:
    def init(self, cid: str, message: str, session_id: str = "", v: bool = False):
        session_id = session_id or str(uuid4())
        out = sess.post(
            f"{URL}/chatbot/{cid}/prompt",
            json={
                "session_id": session_id,
                "new_message": message,
            },
        )
        if v:
            print(out.json())
        return out.json()

    def chat(self, cid: str):
        print("Hello to fury Chat. Press ctrl+c to exit.")
        print("BOT: Hello, I am a fury chatbot. What can I do for you?")
        sess_id = str(uuid4())
        prompt = input("USR: ")
        while not prompt:
            print("BOT: Please say something")
            prompt = input("USR: ")
        while True:
            out = self.init(cid, prompt, sess_id)
            print("BOT:", out["result"])
            prompt = input("USR: ")
            while not prompt:
                print("BOT: Please say something")
                prompt = input("USR: ")

    def get(self, cid: str, pid: str, v: bool = False):
        out = sess.get(f"{URL}/chatbot/{cid}/prompt/{pid}")
        if v:
            print(out.json())
        return out.json()

    def delete(self, cid: str, pid: str, v: bool = False):
        out = sess.delete(f"{URL}/chatbot/{cid}/prompt/{pid}")
        if v:
            print(out.json())
        return out.json()

    def list(self, cid: str, limit: int = 0, offset: int = 0, v: bool = False):
        out = sess.get(f"{URL}/chatbot/{cid}/prompt?limit={limit}&offset={offset}")
        if v:
            print(out.json())
        return out.json()


if __name__ == "__main__":
    fire.Fire(
        {
            "auth": AuthAPI,
            "chatbot": ChatbotAPI,
            "fury": FuryAPI,
            "prompts": PromptsAPI,
        }
    )

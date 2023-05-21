import os
import fire
from requests import Session


def hr(msg: str = ""):
    width = os.get_terminal_size().columns
    if len(msg) > width - 5:
        print("=" * width)
        print(msg)
        print("=" * width // 2)  # type: ignore
    else:
        print("=" * (width - len(msg) - 1) + " " + msg)


TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Inlhc2hib25kZSIsInVzZXJpZCI6Imk3Z2ZxcnJ6In0.GXVe_TGkr-35OcVWSSMxG9Ewh7gVJ_A1Zt4IOqEpmY8"
URL = "http://127.0.0.1:8000/api/v1"

sess = Session()
sess.headers.update({"token": TOKEN})


class ChatbotAPI:
    def init(self, name: str, v: bool = False):
        out = sess.post(f"{URL}/chatbot/", json={"name": name, "dag": {}})
        if v:
            print(out.json())
        return out.json()

    def show(self, id: str, v: bool = False):
        out = sess.get(f"{URL}/chatbot/{id}")
        if v:
            print(out.json())
        return out.json()

    def update(self, id: str, name: str, dag: dict, v: bool = False):
        out = sess.put(f"{URL}/chatbot/{id}", json={"name": name, "dag": dag})
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
        # I hate black and its useless rules, stories are usually so readable and this has no mercy
        # I dislike it my core, this is against an individuals idea of pretty code looks like. This
        # is absolutely evil
        hr("Create chatbot")
        out = self.init(name)
        print("New chatbot:", out)
        # ----
        hr("List chatbots")
        out = self.list()["chatbots"]
        print("total chatbots:", len(out))
        # ----
        hr("Show chatbot")
        out = self.show(out[0]["id"])
        print("chatbot:", out)
        # ----
        hr("Update chatbot")
        out = self.update(out["id"], name="new name", dag={"key": "value"})
        print("updated chatbot:", out)
        # ----
        hr("Delete chatbot")
        out = self.delete(out["id"])
        print("deleted chatbot:", out)
        # ----
        hr("List chatbots")
        out = self.list()
        print("total chatbots:", len(out))


class FuryAPI:
    def comp(self, v: bool = False):
        out = sess.get(f"{URL}/fury/components/")
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


if __name__ == "__main__":
    fire.Fire({"chatbot": ChatbotAPI, "fury": FuryAPI})

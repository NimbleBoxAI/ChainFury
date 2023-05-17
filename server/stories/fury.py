import json
from pprint import pprint

from fury import Node, NodeConnection, TemplateField

print(Node)

with open("./stories/dag.json", "r") as f:
    data = json.load(f)

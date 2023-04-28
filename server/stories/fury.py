import json
from pprint import pprint

from fury import Node, NodeConnection, TemplateField, Dag

with open("./stories/dag.json", "r") as f:
    data = json.load(f)

# def convert_langflow_dag_to_fury(dag):
#     nodes = []
#     edges = []
#     for node in dag["nodes"]:
#         nodes.append(Node.from_json(node))
#     for edge in dag["edges"]:
#         edges.append(Edge.from_json(edge))
#     return Dag(nodes=nodes, edges=edges)

dag = Dag.from_dict(data)
print(dag)

print(dag.to_dict())

# dag.build()

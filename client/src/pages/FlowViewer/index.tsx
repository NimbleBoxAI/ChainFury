import React, { useState, useRef, useCallback } from "react";
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Connection,
  Edge,
  Handle,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";
import { ChainFuryNode } from "../../components/ChainFuryNode";

export const nodeTypes = { ChainFuryNode: ChainFuryNode };

const FlowViewer = () => {
  const reactFlowWrapper = useRef(null) as any;
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(
    null as null | {
      project: (arg0: { x: number; y: number }) => { x: number; y: number };
    }
  );

  const onConnect = useCallback(
    (params: Edge<any> | Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  const onDragOver = useCallback(
    (event: {
      preventDefault: () => void;
      dataTransfer: { dropEffect: string };
    }) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
    },
    []
  );

  const onDrop = useCallback(
    (event: {
      preventDefault: () => void;
      dataTransfer: { getData: (arg0: string) => any };
      clientX: number;
      clientY: number;
    }) => {
      event.preventDefault();
      if (reactFlowInstance?.project && reactFlowWrapper?.current) {
        const reactFlowBounds =
          reactFlowWrapper?.current?.getBoundingClientRect();
        const type = event.dataTransfer.getData("application/reactflow");

        // check if the dropped element is valid
        if (typeof type === "undefined" || !type) {
          return;
        }

        const position = reactFlowInstance.project({
          x: event.clientX - reactFlowBounds.left,
          y: event.clientY - reactFlowBounds.top,
        });
        const newNode = {
          id: type,
          position,
          type: "ChainFuryNode",
          data: {
            node: {
              template: {
                path: {
                  required: true,
                  placeholder: "",
                  show: true,
                  multiline: false,
                  value: "",
                  suffixes: [".csv"],
                  fileTypes: ["csv"],
                  password: false,
                  name: "path",
                  type: "file",
                  list: false,
                  content: null,
                },
                llm: {
                  required: true,
                  placeholder: "",
                  show: true,
                  multiline: false,
                  password: false,
                  name: "llm",
                  type: "BaseLanguageModel",
                  list: false,
                },
                _type: "csv_agent",
              },
              description: "Construct a json agent from a CSV and tools.",
              base_classes: ["AgentExecutor"],
            },
            id: "newId",
            value: null,
          },
        };

        setNodes((nds) => nds.concat(newNode));
      }
    },
    [reactFlowInstance]
  );

  return (
    <div className=" w-full">
      <ReactFlowProvider>
        <div className=" w-[calc(100vw-250px)] h-full" ref={reactFlowWrapper}>
          <ReactFlow
            nodeTypes={nodeTypes}
            proOptions={{ hideAttribution: true }}
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            defaultViewport={{
              zoom: 1,
              y: 0,
              x: 0,
            }}
          >
            <Controls />
          </ReactFlow>
        </div>
      </ReactFlowProvider>
    </div>
  );
};

export default FlowViewer;

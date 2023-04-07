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

let id = 0;
const getId = () => `dndnode_${id++}`;

export const ChainFuryNode = (props: { data: { label: string } }) => {
  return (
    <div
      className={`min-w-[100px] border border-light-neutral-grey-200 rounded-[4px] shadow-sm bg-light-system-bg-primary`}
    >
      <div className="flex flex-col">
        <div className="p-[8px] bg-light-primary-blue-400 medium350">
          <span className="semiBold250 text-white">{props.data.label}</span>
        </div>
        <input className="h-[24px] m-[8px]" placeholder="something" />
        <input className="h-[24px] m-[8px]" placeholder="something" />
        <input className="h-[24px] m-[8px]" placeholder="something" />
      </div>
      <Handle
        className="border-0"
        type="source"
        position={Position.Right}
        id="a"
      />
    </div>
  );
};

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
          id: getId(),
          position,
          type: "ChainFuryNode",
          data: { label: `${type} node` },
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
            fitView
          >
            <Controls />
          </ReactFlow>
        </div>
      </ReactFlowProvider>
    </div>
  );
};

export default FlowViewer;

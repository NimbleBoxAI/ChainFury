import { useRef, useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  ReactFlowInstance,
  Edge,
  Connection,
  addEdge,
  ReactFlowProvider,
  Controls
} from 'reactflow';
import { furyNodeTypes } from '../../pages/FlowViewer';

const FuryFlowViewer = ({
  nodes,
  setNodes,
  onNodesChange,
  edges,
  setEdges,
  onEdgesChange
}: {
  nodes: any;
  setNodes: any;
  onNodesChange: any;
  edges: any;
  setEdges: any;
  onEdgesChange: any;
}) => {
  const reactFlowWrapper = useRef(null) as any;
  const [reactFlowInstance, setReactFlowInstance] = useState(null as null | ReactFlowInstance);
  const initialNodes = [
    {
      id: 'chatin',
      position: { x: 0, y: 0 },
      data: { label: 'Chat In' },
      deletable: false,
      type: 'input'
    },
    {
      id: 'chatout',
      position: { x: 0, y: 100 },
      data: { label: 'Chat Out' },
      deletable: false,
      type: 'output'
    }
  ];

  useEffect(() => {
    setNodes(initialNodes);
  }, []);

  const onDrop = useCallback(
    (event: {
      preventDefault: () => void;
      dataTransfer: { getData: (arg0: string) => any };
      clientX: number;
      clientY: number;
    }) => {
      event.preventDefault();
      if (reactFlowInstance?.project && reactFlowWrapper?.current) {
        let type = event.dataTransfer.getData('application/reactflow');
        const reactFlowBounds = reactFlowWrapper?.current?.getBoundingClientRect();
        const nodeData = JSON.parse(type);
        const position = reactFlowInstance?.project({
          x: event.clientX - reactFlowBounds.left,
          y: event.clientY - reactFlowBounds.top
        });
        const newId = nodeData.id + '_' + Math.random() * 100000;
        const newNode = {
          id: newId,
          cf_id: nodeData.id,
          position,
          type: 'FuryEngineNode',
          data: {
            type: nodeData.type,
            node: nodeData,
            id: nodeData.id,
            value: null,
            deleteMe: () => {
              setNodes((nds: any[]) => nds.filter((delnode: { id: any }) => delnode.id !== newId));
            }
          }
        } as any;

        setNodes((nds: string | any[]) => nds.concat(newNode));
      }
    },
    [reactFlowInstance]
  );

  const onDragOver = useCallback(
    (event: { preventDefault: () => void; dataTransfer: { dropEffect: string } }) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    },
    []
  );

  const onConnect = useCallback(
    (params: Edge<any> | Connection) => setEdges((eds: Edge[]) => addEdge(params, eds)),
    []
  );

  return (
    <>
      <ReactFlowProvider>
        <div className=" w-[calc(100vw-250px)] h-full" ref={reactFlowWrapper}>
          <ReactFlow
            nodeTypes={furyNodeTypes}
            proOptions={{ hideAttribution: true }}
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            fitView={true}
            defaultViewport={{
              zoom: 0.8,
              y: 0,
              x: 0
            }}
          >
            <Controls />
          </ReactFlow>
        </div>
      </ReactFlowProvider>
    </>
  );
};

export default FuryFlowViewer;

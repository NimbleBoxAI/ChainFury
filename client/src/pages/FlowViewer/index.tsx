import { Button } from '@mui/material';
import { useState, useRef, useCallback, useEffect } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Connection,
  Edge,
  ReactFlowInstance
} from 'reactflow';
import 'reactflow/dist/style.css';
import { ChainFuryNode } from '../../components/ChainFuryNode';
import { FuryEngineNode } from '../../components/FuryEngineNode';
import ChatComp from '../../components/ChatComp';
import { useAuthStates } from '../../redux/hooks/dispatchHooks';
import { useAppDispatch } from '../../redux/hooks/store';
import {
  useComponentsMutation,
  useCreateBotMutation,
  useEditBotMutation,
  useFuryComponentDetailsMutation,
  useFuryComponentsMutation
} from '../../redux/services/auth';
import { setComponents, setFuryComponents } from '../../redux/slices/authSlice';
import FuryFlowViewer from '../../components/fury/FuryFlowViewer';
import { TranslateNodes } from '../../utils';

export const nodeTypes = { ChainFuryNode: ChainFuryNode };
export const furyNodeTypes = { FuryEngineNode: FuryEngineNode };

const FlowViewer = () => {
  const reactFlowWrapper = useRef(null) as any;
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true as boolean);
  const [reactFlowInstance, setReactFlowInstance] = useState(null as null | ReactFlowInstance);
  const [variant, setVariant] = useState('' as 'new' | 'edit' | 'template');
  const { flow_id } = useParams() as {
    flow_id: string;
  };
  const [botName, setBotName] = useState('' as string);
  const [getComponents] = useComponentsMutation();
  const [getFullComponents] = useFuryComponentsMutation();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const [templateId, setTemplateId] = useState('' as string);
  const [createBot] = useCreateBotMutation();
  const [editBot] = useEditBotMutation();
  const [furyCompDetails] = useFuryComponentDetailsMutation();
  const { auth } = useAuthStates();
  const [engine, setEngine] = useState('' as '' | 'fury' | 'langflow');

  useEffect(() => {
    setEngine((location.search.split('&engine=')[1] as 'fury' | 'langflow') || 'langflow');
    if (location.search?.includes('?bot=') && flow_id === 'new') {
      setBotName(location.search.split('?bot=')[1]?.split('&engine=')[0]);
      setVariant('new');
      setNodes([]);
      setEdges([]);
      setLoading(false);
    } else if (flow_id === 'template' && location.search?.includes('?bot=')) {
      setBotName(location.search.split('?bot=')[1]?.split('&id=')[0]);
      setTemplateId(location.search.split('&id=')[1]);
      setVariant('template');
    } else {
      setVariant('edit');
    }
  }, [location]);

  useEffect(() => {
    if (engine) fetchComponents();
  }, [engine]);

  useEffect(() => {
    if ((auth?.chatBots?.[flow_id] || auth.templates?.[templateId]) && variant) {
      setLoading(false);
      createNodesForExistingBot();
    }
  }, [auth.chatBots, location, auth.templates, templateId, variant]);

  const fetchComponents = async () => {
    if (engine !== 'fury')
      getComponents()
        .unwrap()
        .then((res) => {
          dispatch(
            setComponents({
              components: res
            })
          );
        })
        ?.catch(() => {
          alert('Error fetching components');
        });
    else {
      const furyConfig = await getFullComponents().unwrap();
      const components = {} as any;
      if (furyConfig?.components) {
        for (let i = 0; i < furyConfig?.components?.length; i++) {
          await furyCompDetails({
            component_type: furyConfig?.components[i]
          })
            .unwrap()
            .then((res) => {
              console.log({ [furyConfig?.components[i]]: res });
              components[furyConfig?.components[i]] = {
                components: Object.values(res),
                type: furyConfig?.components[i]
              };
            });
        }
      }
      if (furyConfig?.actions) {
        components['actions'] = {
          components: []
        };
      }
      dispatch(
        setFuryComponents({
          furyComponents: components
        })
      );
    }
  };

  const onConnect = useCallback(
    (params: Edge<any> | Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  const onDragOver = useCallback(
    (event: { preventDefault: () => void; dataTransfer: { dropEffect: string } }) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
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
        const reactFlowBounds = reactFlowWrapper?.current?.getBoundingClientRect();
        let type = event.dataTransfer.getData('application/reactflow');
        const nodeData = JSON.parse(type);
        type = nodeData?.displayName;
        // check if the dropped element is valid
        if (typeof type === 'undefined' || !type) {
          return;
        }

        const position = reactFlowInstance.project({
          x: event.clientX - reactFlowBounds.left,
          y: event.clientY - reactFlowBounds.top
        });
        const newNode = {
          id: type,
          position,
          type: 'ChainFuryNode',
          data: {
            type: type,
            node: nodeData,
            id: type,
            value: null,
            deleteMe: () => {
              setNodes((nds) => nds.filter((node) => node.id !== type));
            }
          }
        };

        setNodes((nds) => nds.concat(newNode));
      }
    },
    [reactFlowInstance]
  );

  const createChatBot = () => {
    createBot(
      engine === 'langflow'
        ? { name: botName, nodes, edges, token: auth?.accessToken, engine: engine }
        : {
            name: botName,
            engine: engine,
            token: auth?.accessToken,
            ...TranslateNodes({ nodes, edges })
          }
    )
      .unwrap()
      ?.then((res) => {
        if (res?.id) window.location.href = '/ui/dashboard/' + res?.id;
        else {
          alert('Error creating bot');
        }
      })
      .catch((err) => {
        console.log(err);
        alert('Error creating bot');
      });
  };

  const createNodesForExistingBot = () => {
    (variant === 'edit'
      ? auth.chatBots?.[flow_id]
      : auth?.templates?.[templateId]
    )?.dag?.nodes?.forEach((node: any) => {
      const newNode = {
        id: node?.id ?? '',
        position: node?.position ?? { x: 0, y: 0 },
        type: 'ChainFuryNode',
        data: {
          type: node?.id,
          ...node?.data,
          node: JSON.parse(JSON.stringify(node?.data?.node)),
          deleteMe: () => {
            setNodes((nds) => nds.filter((delnode) => delnode.id !== node?.id));
          }
        }
      };
      setNodes((nds) => nds.concat(newNode));
    });
    setEdges(
      (variant === 'edit' ? auth.chatBots?.[flow_id] : auth?.templates?.[templateId])?.dag?.edges
    );
  };

  const editChatBot = () => {
    editBot({
      id: flow_id,
      name: auth?.chatBots?.[flow_id]?.name,
      nodes,
      edges,
      token: auth?.accessToken
    })
      .unwrap()
      ?.then((res) => {
        alert('Bot edited successfully');
      })
      .catch((err) => {
        alert('Error editing bot');
      });
  };

  return (
    <div className=" w-full max-h-screen flex flex-col overflow-hidden prose-nbx">
      <div className="p-[16px] border-b border-light-neutral-grey-200 semiBold350">
        {variant === 'new'
          ? 'Start building your flow by dragging and dropping nodes from the left panel'
          : 'Edit your flow by dragging and dropping nodes from the left panel'}
        <Button
          className="h-[28px]"
          variant="outlined"
          color="primary"
          onClick={() => {
            if (variant === 'new' || variant === 'template') {
              createChatBot();
            } else {
              editChatBot();
            }
          }}
          sx={{ float: 'right' }}
        >
          {variant === 'new' ? 'Create' : 'Save'}
        </Button>
      </div>
      {!loading ? (
        engine === 'langflow' ? (
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
        ) : (
          <FuryFlowViewer
            nodes={nodes}
            setNodes={setNodes}
            onNodesChange={onNodesChange}
            edges={edges}
            setEdges={setEdges}
            onEdgesChange={onEdgesChange}
          />
        )
      ) : (
        ''
      )}
      {flow_id && variant === 'edit' ? (
        <div className="h-[450px] w-[350px] absolute bottom-0 right-0">
          <ChatComp chatId={flow_id} />
        </div>
      ) : (
        ''
      )}
    </div>
  );
};

export default FlowViewer;

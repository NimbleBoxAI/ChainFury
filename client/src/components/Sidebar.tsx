import { Button, Collapse } from '@mui/material';
import { useContext, useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useAuthStates } from '../redux/hooks/dispatchHooks';
import { useAppDispatch } from '../redux/hooks/store';
import {
  useGetActionsMutation,
  useGetBotsMutation,
} from '../redux/services/auth';
import {
  FuryComponentInterface,
  setChatBots,
  setFuryCompKey,
  setSelectedChatBot,
  setTemplates
} from '../redux/slices/authSlice';
import ChangePassword from './ChangePassword';
import ChatBotCard from './ChatBotCard';
import CollapsibleComponents from './CollapsibleComponents';
import NewBotModel from './NewBotModel';
import { nodeColors } from '../utils';
import SvgChevronDown from './SvgComps/ChevronDown';
import NewActionModel from './NewActionModel';
import { ChainFuryContext } from '../App';

const Sidebar = () => {
  const [newBotModel, setNewBotModel] = useState(false);
  const { flow_id } = useParams();
  const navigate = useNavigate();
  const { auth } = useAuthStates();
  const [getBots] = useGetBotsMutation();
  const dispatch = useAppDispatch();
  const [changePassword, setChangePassword] = useState(false);
  const [searchParams] = useSearchParams();
  const { engine, setEngine } = useContext(ChainFuryContext);
  const location = useLocation();
  const [newAction, setNewAction] = useState(false);
  const [getFuryActions] = useGetActionsMutation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const engine = params.get('engine');
    setEngine(engine ?? 'fury');
  }, [location.search]);

  useEffect(() => {
    if (!localStorage.getItem('accessToken')) {
      navigate('/ui/login');
    } else {
      getBotList();
    }
  }, []);

  useEffect(() => {
    // if (!Object.values(auth.furyComponents?.['actions'] ?? {})?.length) getActions();
  }, [auth.furyComponents]);

  const getBotList = () => {
    getBots({
      token: auth?.accessToken
    })
      .unwrap()
      .then((res) => {
        dispatch(
          setChatBots({
            chatBots: res?.chatbots?.length ? res?.chatbots : []
          })
        );
        if (!searchParams?.get('id')) {
          dispatch(setSelectedChatBot({ chatBot: res?.chatbots[0] }));
          navigate(`/ui/dashboard/?id=${res?.chatbots[0]?.id ?? ''}`);
        }
      })
      .catch((err) => {
        console.log(err);
      });

  };

  const onDragStart = (
    event: {
      dataTransfer: {
        setData: (arg0: string, arg1: any) => void;
        effectAllowed: string;
      };
    },
    nodeType: any
  ) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const getActions = () => {
    getFuryActions({})
      .unwrap()
      .then((res) => {
        dispatch(
          setFuryCompKey({
            key: 'actions',
            component: res
          })
        );
      });
  };

  return (
    <div className="relative overflow-hidden w-[250px] min-w-[250px] border-r h-screen shadow-sm bg-light-system-bg-secondary p-[8px] prose-nbx">
      {newBotModel ? <NewBotModel onClose={() => setNewBotModel(false)} /> : ''}
      {flow_id ? (
        <div className="flex flex-col">
          <Button
            onClick={() => navigate('/ui/dashboard')}
            variant="outlined"
            className="my-[8px!important]"
            color="primary"
            fullWidth
          >
            Go Back
          </Button>
          {engine === 'fury' ? (
            <Button
              onClick={() => {
                setNewAction(true);
              }}
              variant="outlined"
              className="my-[8px!important] border-light-success-green-600"
              color="primary"
              fullWidth
            >
              + Action
            </Button>
          ) : (
            ''
          )}
        </div>
      ) : (
        // <Button
        //   onClick={() => setNewBotModel(true)}
        //   variant="contained"
        //   className="my-[8px!important]"
        //   color="primary"
        //   fullWidth
        // >
        "New Bot"
        // </Button>
        // ''
      )}
      {newAction ? <NewActionModel refresh={getActions} onClose={() => setNewAction(false)} /> : ''}

      <div className="overflow-scroll max-h-[calc(100%-120px)]">
        {!flow_id ? (
          <>
            <div className="flex flex-col gap-[8px]">
              <div className='border-b border-light-neutral-grey-200 pb-[10px]'></div>
              <span className="semiBold700 text-light-neutral-grey-900">🦋 Chains</span>
              {Object.values(auth?.chatBots ?? [])?.map((bot, key) => {
                return (
                  <div
                    key={key}
                    onClick={() => {
                      dispatch(
                        setSelectedChatBot({
                          chatBot: bot
                        })
                      );
                      navigate(`/ui/dashboard/?id=${bot?.id ?? ''}`);
                    }}
                  >
                    <ChatBotCard key={key} label={bot?.name} />
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <div className="flex flex-col gap-[8px]">
            {/* Langchain */}
            {engine === 'langchain'
              ? Object.keys(auth?.components).map((bot, key) => {
                return (
                  <CollapsibleComponents
                    key={key}
                    label={bot}
                    onDragStart={onDragStart}
                    values={auth?.components[bot]}
                  />
                );
              })
              : Object.keys(auth?.furyComponents).map((bot, key) => {
                return (
                  <FuryCollapsibleComponents
                    key={key}
                    label={bot}
                    values={auth?.furyComponents[bot]?.components ?? []}
                    onDragStart={onDragStart}
                  />
                );
              })}
          </div>
        )}
      </div>
      <div className="h-[78x] absolute bottom-0 flex flex-col gap-[4px]">
        <a
          href={
            window?.location?.host?.includes(':5173')
              ? 'http://127.0.0.1:8000/docs'
              : '/docs'
          }
          target='_blank'
          className="medium400 cursor-pointer"
        >
          Swagger
        </a>
        <span
          className="medium400 cursor-pointer"
        >
          <button
            onClick={() => {
              // copy JWT token to clipboard
              navigator.clipboard.writeText(localStorage.getItem('accessToken') ?? '');
            }}
          >Copy Token</button>
        </span>
        <a
          href="https://nimbleboxai.github.io/ChainFury/"
          target='_blank'
          className="medium400 cursor-pointer"
        >
          Documentation
        </a>
        <span
          className="medium400 cursor-pointer"
          onClick={() => {
            setChangePassword(true);
          }}
        >
          Change Password
        </span>
        <span
          onClick={() => {
            localStorage.clear();
            navigate('/ui/login');
          }}
          className="medium400 cursor-pointer"
        >
          Log Out
        </span>
      </div>
      {changePassword ? (
        <ChangePassword
          onClose={() => {
            setChangePassword(false);
          }}
        />
      ) : (
        ''
      )}
    </div>
  );
};

export default Sidebar;

const FuryCollapsibleComponents = ({
  label,
  values,
  onDragStart
}: {
  label: string;
  values: FuryComponentInterface[];
  onDragStart: {
    (
      event: {
        dataTransfer: {
          setData: (arg0: string, arg1: any) => void;
          effectAllowed: string;
        };
      },
      nodeType: any
    ): void;
    (event: any, nodeType: any): void;
  };
}) => {
  const [open, setOpen] = useState(false);

  return (
    <Collapse in={open} collapsedSize={42}>
      <div
        onClick={() => {
          setOpen(!open);
        }}
        className="prose-nbx cursor-pointer medium400 border border-light-neutral-grey-200 rounded-md bg-light-system-bg-primary"
      >
        <div className="p-[8px] flex justify-between items-center">
          <span className="capitalize semiBold300">{label}</span>{' '}
          <SvgChevronDown
            style={{
              stroke: nodeColors[label]
            }}
            className={`${open ? 'rotate-180' : ''}`}
          />
        </div>
        <div className="flex flex-col gap-[16px] p-[8px] bg-light-neutral-grey-100">
          {values.map((bot, key) => {
            return (
              <div
                key={key}
                style={{
                  borderLeftColor: nodeColors[label]
                }}
                className="bg-light-system-bg-primary rounded-md p-[4px] border-l-[2px] medium300"
                draggable={label !== 'models'}
                onDragStart={(event) => {
                  onDragStart(event, JSON.stringify(bot));
                }}
              >
                {bot?.name || bot?.id}
              </div>
            );
          })}
        </div>
      </div>
    </Collapse>
  );
};

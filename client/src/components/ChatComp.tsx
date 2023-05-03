import { useEffect, useId, useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { useAddUserFeedBackMutation, useProcessPromptMutation } from '../redux/services/auth';
import { makeid } from '../utils';
import chatImg from '../assets/chatBox.png';
import closeImg from '../assets/close.png';

interface ChatInterface {
  id: number;
  message: string;
  isSender: boolean;
}

const ChatComp = ({ chatId }: { chatId?: string }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chat, setChat] = useState<ChatInterface[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [waiting, setWaiting] = useState(false);
  const { chat_id } = useParams<{ chat_id: string }>();
  const [processPrompt] = useProcessPromptMutation();
  const [usersMessages, setUsersMessages] = useState<string[]>([]);
  const [enableFeedback, setEnableFeedback] = useState(false);
  const [addFeedback] = useAddUserFeedBackMutation();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const location = useLocation();

  useEffect(() => {
    if (chatId) {
      setChat([]);
      setUsersMessages([]);
      setSessionId(makeid(30));
      setIsChatOpen(false);
    }
  }, [chatId]);

  useEffect(() => {
    console.log('location changed', location.hash);
    if (location.hash === '#open') {
      setIsChatOpen(true);
    } else {
      setIsChatOpen(false);
    }
  }, [location]);

  useEffect(() => {
    if (currentMessage?.trim()) handleProcessPrompt();
  }, [chat]);

  const handleProcessPrompt = async () => {
    setEnableFeedback(false);
    setWaiting(true);
    processPrompt({
      chatbot_id: chatId ?? chat_id ?? '',
      new_message: currentMessage,
      chat_history: usersMessages,
      session_id: sessionId ?? ''
    })
      .unwrap()
      .then((res) => {
        setChat([
          ...chat,
          {
            id: res?.prompt_id,
            message: res?.result,
            isSender: false
          }
        ]);
        setEnableFeedback(true);
      })
      .catch((err) => {
        if (err?.data?.detail)
          setChat([
            ...chat,
            {
              id: chat.length + 1,
              message: err?.data?.detail,
              isSender: false
            }
          ]);
      })
      .finally(() => {
        // scroll to bottom
        const chatContainer = document.querySelector('.chatContainer');
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight - 300;
        }
        setUsersMessages([...usersMessages, currentMessage]);
        setWaiting(false);
      });
    setCurrentMessage('');
  };

  const handleFeedback = (feedback: number, promptId: string) => {
    addFeedback({
      prompt_id: promptId,
      score: feedback
    }).finally(() => {
      setEnableFeedback(false);
    });
  };

  return (
    <div
      className={`absolute z-[100000] right-0 bottom-0 pt-[8px] px-[4px] ${
        chat_id ? 'w-screen' : ''
      } overflow-hidden`}
    >
      <div
        className={`flex flex-col ${
          isChatOpen && !chatId ? (chat_id ? 'w-[98vw]' : 'w-[350px]') : ''
        } ${chatId ? 'max-h-[450px]' : 'max-h-screen'} ${
          isChatOpen ? 'border shadow-md overflow-hidden mr-[4px]' : ''
        } border-light-neutral-grey-200 rounded-md  regular250 `}
      >
        {isChatOpen ? (
          <>
            <div className="overflow-scroll  bg-light-system-bg-primary h-[420px] min-w-[350px] p-[16px] pb-[40px] chatContainer">
              <div className="chat nbx-chat-start">
                <div className={`flex flex-col `}>
                  <div className={`chat-bubble`}>Hi there! How can I help?</div>
                </div>
              </div>
              {chat.map((chatVal, key) => (
                <div
                  key={key}
                  className={`chat ${chatVal.isSender ? 'nbx-chat-end' : 'nbx-chat-start'}`}
                >
                  <div
                    className={`flex flex-col ${
                      !chatVal?.isSender && enableFeedback
                        ? 'rounded-b-[8px!important] overflow-hidden'
                        : ''
                    }`}
                  >
                    <div
                      className={`chat-bubble ${
                        !chatVal?.isSender && enableFeedback ? 'rounded-br-[0px!important]' : ''
                      }`}
                    >
                      {chatVal.message}
                    </div>
                    {!chatVal?.isSender && enableFeedback && key === chat?.length - 1 ? (
                      <div className="bg-light-neutral-grey-300 p-[8px] flex gap-[8px] text-light-neutral-grey-900 items-center">
                        <span>Rate this answer:</span>
                        <span
                          onClick={() => {
                            handleFeedback(3, chatVal.id.toString());
                          }}
                          className="text-[20px] cursor-pointer"
                        >
                          😀
                        </span>
                        <span
                          onClick={() => {
                            handleFeedback(2, chatVal.id.toString());
                          }}
                          className="text-[20px] cursor-pointer"
                        >
                          😐
                        </span>
                        <span
                          onClick={() => {
                            handleFeedback(1, chatVal.id.toString());
                          }}
                          className="text-[20px] cursor-pointer"
                        >
                          😞
                        </span>
                      </div>
                    ) : (
                      ''
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="p-[8px] bg-light-system-bg-primary ">
              <input
                value={waiting ? 'Thinking...' : currentMessage}
                disabled={waiting}
                onChange={(e) => {
                  setCurrentMessage(e.target.value);
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && currentMessage?.trim()) {
                    setChat([
                      ...chat,
                      {
                        id: chat.length + 1,
                        message: currentMessage,
                        isSender: true
                      }
                    ]);
                  }
                }}
                type="text"
                placeholder="Write your message!"
                className="w-full focus:outline-none pl bg-light-system-bg-secondary rounded-md py-3"
              />
            </div>
          </>
        ) : (
          <div className="flex justify-end">
            <div
              onClick={() => {
                setIsChatOpen(true);
              }}
              className={`w-fit rounded-full m-[16px] border-0 cursor-pointer p-[8px] bg-light-primary-blue-400`}
            >
              <img src={chatImg} alt="chat_box" className="w-[30px] h-[30px]" />
            </div>
          </div>
        )}
      </div>
      <div className="flex justify-end">
        {isChatOpen ? (
          <div
            onClick={() => {
              setIsChatOpen(false);
            }}
            className={`w-fit rounded-full m-[16px] mt-[8px] border-0 cursor-pointer p-[8px] bg-light-critical-red-600`}
          >
            <img src={closeImg} alt="chat_box" className="w-[30px] h-[30px]" />
          </div>
        ) : (
          ''
        )}
      </div>
    </div>
  );
};

export default ChatComp;

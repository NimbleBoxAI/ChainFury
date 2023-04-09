import { useState } from "react";

const dummyChat = [
  {
    id: 1,
    message: "Hey, have you seen the latest episode of Rick and Morty?",
    isSender: true,
  },
  {
    id: 2,
    message: "No, not yet. Is it good?",
    isSender: false,
  },
  {
    id: 3,
    message:
      "Yeah, it's pretty wild. Lots of crazy stuff happens. You gotta check it out.",
    isSender: true,
  },
  {
    id: 4,
    message: "Sounds interesting. I'll watch it tonight.",
    isSender: false,
  },
  {
    id: 5,
    message:
      "Cool. Let me know what you think. I'm still trying to figure out what the heck was going on in that episode.",
    isSender: true,
  },
  {
    id: 6,
    message:
      "Haha, will do. You know, I still can't decide who's my favorite character: Rick or Morty.",
    isSender: false,
  },
  {
    id: 7,
    message:
      "Right? They're both so different but so awesome in their own ways. It's hard to choose.",
    isSender: true,
  },
  {
    id: 8,
    message:
      "I think I like Morty more, though. He's just so relatable sometimes.",
    isSender: false,
  },
  {
    id: 9,
    message:
      "Yeah, I can see that. But Rick's just so freaking cool. He's always doing crazy stuff and going on adventures.",
    isSender: true,
  },
  {
    id: 10,
    message:
      "True, true. Anyway, I'm gonna go watch that episode now. Thanks for the heads up!",
    isSender: false,
  },
  {
    id: 11,
    message: "No problem. Let me know if you wanna talk about it afterwards.",
    isSender: true,
  },
];

const ChatComp = ({ chatId }: { chatId?: string }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div className="absolute bg-light-system-bg-primary z-[100000] right-0 bottom-0 ">
      <div
        className={`flex flex-col ${isChatOpen && !chatId ? "w-screen" : ""} ${
          chatId ? "max-h-[450px]" : "max-h-screen"
        } border border-light-neutral-grey-200 shadow-sm rounded-md  regular250 overflow-hidden`}
      >
        <div
          onClick={() => {
            if (!isChatOpen) setIsChatOpen(true);
          }}
          className="cursor-pointer flex justify-between chatHeader semiBold400 p-[8px] border-b bg-light-primary-blue-400 text-white"
        >
          The Bot
          {isChatOpen ? (
            <span
              onClick={() => {
                setIsChatOpen(false);
              }}
              className="cursor-pointer"
            >
              ----
            </span>
          ) : (
            ""
          )}
        </div>
        {isChatOpen ? (
          <>
            <div className="overflow-scroll h-full p-[16px]">
              {dummyChat.map((chat) => (
                <div
                  key={chat.id}
                  className={`chat ${
                    chat.isSender ? "nbx-chat-end" : "nbx-chat-start"
                  }`}
                >
                  <div className="chat-bubble">{chat.message}</div>
                </div>
              ))}
            </div>
            <div className="p-[8px]">
              <input
                type="text"
                placeholder="Write your message!"
                className="w-full focus:outline-none pl bg-light-system-bg-secondary rounded-md py-3"
              />
            </div>
          </>
        ) : (
          ""
        )}
      </div>
    </div>
  );
};

export default ChatComp;

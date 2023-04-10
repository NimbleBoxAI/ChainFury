import { useAuthStates } from "../redux/hooks/dispatchHooks";

const ChatBotCard = ({ label }: { label: string }) => {
  const { auth } = useAuthStates();

  return (
    <div
      className={`${
        auth?.selectedChatBot?.name === label
          ? "border-light-primary-blue-400 border-2 bg-light-primary-blue-50"
          : ""
      } p-[8px] cursor-pointer medium400 border border-light-neutral-grey-200 rounded-md bg-light-system-bg-primary`}
    >
      {label}
    </div>
  );
};

export default ChatBotCard;

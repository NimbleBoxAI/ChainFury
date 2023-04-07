const ChatBotCard = ({ label }: { label: string }) => {
  return (
    <div className="p-[8px] cursor-pointer medium400 border border-light-neutral-grey-200 rounded-md bg-light-system-bg-primary">
      {label}
    </div>
  );
};

export default ChatBotCard;

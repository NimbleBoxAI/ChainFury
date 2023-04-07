import { Button } from "@mui/material";
import ChatBotCard from "./ChatBotCard";

const dummyBots = ["Bot 1", "Bot 2", "Bot 3"];
const dummyTemplates = ["Template 1", "Template 2", "Template 3"];

const Sidebar = () => {
  return (
    <div className="w-[250px] border-r h-screen shadow-sm bg-light-system-bg-secondary p-[8px] prose-nbx">
      <Button
        variant="contained"
        className="my-[8px!important]"
        color="primary"
        fullWidth
      >
        New Bot
      </Button>
      <div className="flex flex-col gap-[8px]">
        <span className="semiBold250 text-light-neutral-grey-900">Bots</span>
        {dummyBots.map((bot, key) => {
          return <ChatBotCard key={key} label={bot} />;
        })}
      </div>
      <div className="flex flex-col gap-[8px] mt-[16px]">
        <span className="semiBold250 text-light-neutral-grey-900">
          Templates
        </span>
        {dummyTemplates.map((bot, key) => {
          return <ChatBotCard key={key} label={bot} />;
        })}
      </div>
    </div>
  );
};

export default Sidebar;

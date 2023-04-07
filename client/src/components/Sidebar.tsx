import { Button } from "@mui/material";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ChatBotCard from "./ChatBotCard";
import NewBotModel from "./NewBotModel";

const dummyBots = ["Bot 1", "Bot 2", "Bot 3"];
const dummyTemplates = ["Template 1", "Template 2", "Template 3"];
const dummyChain = ["Chain 1", "Chain 2", "Chain 3"];

const Sidebar = () => {
  const [newBotModel, setNewBotModel] = useState(false);
  const { flow_id } = useParams();

  const onDragStart = (
    event: {
      dataTransfer: {
        setData: (arg0: string, arg1: any) => void;
        effectAllowed: string;
      };
    },
    nodeType: any
  ) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div className="w-[250px] min-w-[250px] border-r h-screen shadow-sm bg-light-system-bg-secondary p-[8px] prose-nbx">
      {newBotModel ? <NewBotModel onClose={() => setNewBotModel(false)} /> : ""}
      <Button
        onClick={() => setNewBotModel(true)}
        variant="contained"
        className="my-[8px!important]"
        color="primary"
        fullWidth
      >
        New Bot
      </Button>
      {!flow_id ? (
        <>
          <div className="flex flex-col gap-[8px]">
            <span className="semiBold250 text-light-neutral-grey-900">
              Bots
            </span>
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
        </>
      ) : (
        <div className="flex flex-col gap-[8px]">
          <span className="semiBold250 text-light-neutral-grey-900">
            Chains
          </span>
          {dummyChain.map((bot, key) => {
            return (
              <div
                className="p-[8px] cursor-pointer medium400 border border-light-neutral-grey-200 rounded-md bg-light-system-bg-primary"
                key={key}
                onDragStart={(event) => onDragStart(event, bot)}
                draggable
              >
                {bot}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Sidebar;

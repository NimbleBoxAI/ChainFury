import { Button, Collapse } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuthStates } from "../redux/hooks/dispatchHooks";
import ChatBotCard from "./ChatBotCard";
import CollapsibleComponents from "./CollapsibleComponents";
import NewBotModel from "./NewBotModel";

const dummyBots = ["Bot 1", "Bot 2", "Bot 3"];
const dummyTemplates = ["Template 1", "Template 2", "Template 3"];

const Sidebar = () => {
  const [newBotModel, setNewBotModel] = useState(false);
  const { flow_id } = useParams();
  const navigate = useNavigate();
  const { auth } = useAuthStates();

  useEffect(() => {
    if (!localStorage.getItem("accessToken")) {
      navigate("/login");
    }
  }, []);

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
    <div className="overflow-hidden w-[250px] min-w-[250px] border-r h-screen shadow-sm bg-light-system-bg-secondary p-[8px] prose-nbx">
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
      <div className="overflow-scroll max-h-[calc(100%-60px)]">
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
            {Object.keys(auth?.components).map((bot, key) => {
              return (
                <CollapsibleComponents
                  key={key}
                  label={bot}
                  onDragStart={onDragStart}
                  values={auth?.components[bot]}
                />
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;

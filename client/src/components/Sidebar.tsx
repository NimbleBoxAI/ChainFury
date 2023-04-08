import { Button, Collapse } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { APIClassType } from "../constants";
import { useAuthStates } from "../redux/hooks/dispatchHooks";
import ChatBotCard from "./ChatBotCard";
import NewBotModel from "./NewBotModel";
import SvgChevronDown from "./SvgComps/ChevronDown";

const dummyBots = ["Bot 1", "Bot 2", "Bot 3"];
const dummyTemplates = ["Template 1", "Template 2", "Template 3"];
const dummyChain = ["Chain 1", "Chain 2", "Chain 3"];

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
      <div className="overflow-scroll max-h-full">
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

const CollapsibleComponents = ({
  onDragStart,
  values,
  label,
}: {
  values: Record<string, APIClassType>;
  label: string;
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

  const ComponentCard = ({ label }: { label: string }) => {
    return (
      <div
        className="bg-light-system-bg-primary rounded-md p-[4px] border-l-[2px] border-lime-600 medium300"
        draggable
        onDragStart={(event) => onDragStart(event, label)}
      >
        {label}
      </div>
    );
  };

  return (
    <Collapse in={open} collapsedSize={42}>
      <div className="prose-nbx cursor-pointer medium400 border border-light-neutral-grey-200 rounded-md bg-light-system-bg-primary">
        {console.log({ values })}
        <div
          onClick={() => {
            setOpen(!open);
          }}
          className="p-[8px] flex justify-between items-center"
        >
          <span className="capitalize semiBold300">{label}</span>
          <SvgChevronDown
            className={`stroke-light-neutral-grey-700 ${
              open ? "rotate-180" : ""
            }`}
          />
        </div>
        <div className="flex flex-col gap-[16px] p-[8px] bg-light-neutral-grey-100">
          {Object.keys(values).map((bot, key) => {
            return <ComponentCard key={key} label={bot} />;
          })}
        </div>
      </div>
    </Collapse>
  );
};

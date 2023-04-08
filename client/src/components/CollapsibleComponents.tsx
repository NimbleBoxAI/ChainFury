import { Collapse } from "@mui/material";
import { useState } from "react";
import { APIClassType } from "../constants";
import SvgChevronDown from "./SvgComps/ChevronDown";

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

export default CollapsibleComponents;

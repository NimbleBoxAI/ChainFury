import { Button, Dialog } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import SvgClose from "./SvgComps/Close";

const NewBotModel = ({ onClose }: { onClose: () => void }) => {
  const navigate = useNavigate();
  const [botName, setBotName] = useState("");

  return (
    <Dialog open={true} onClose={onClose}>
      <div
        className={`prose-nbx relative  gap-[16px] p-[16px] flex flex-col justify-center items-center w-[500px]`}
      >
        <SvgClose className="stroke-light-neutral-grey-900 absolute right-[8px] top-[8px] scale-[1.2] cursor-pointer" />
        <input
          onChange={(e) => {
            setBotName(e.target.value?.replace(" ", "_"));
          }}
          value={botName}
          type="text"
          placeholder="Name"
          className="h-[40px] w-full mt-[16px]"
        />
        <Button
          onClick={() => {
            navigate(`/ui/dashboard/new?bot=${botName}`);
            onClose();
          }}
          variant="contained"
          className="w-full"
        >
          Create
        </Button>
      </div>
    </Dialog>
  );
};

export default NewBotModel;

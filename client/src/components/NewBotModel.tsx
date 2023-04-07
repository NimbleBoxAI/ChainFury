import { Button, Dialog } from "@mui/material";
import SvgClose from "./SvgComps/Close";

const NewBotModel = ({ onClose }: { onClose: () => void }) => {
  return (
    <Dialog open={true} onClose={onClose}>
      <div
        className={`prose-nbx relative  gap-[16px] p-[16px] flex flex-col justify-center items-center w-[500px]`}
      >
        <SvgClose className="stroke-light-neutral-grey-900 absolute right-[8px] top-[8px] scale-[1.2] cursor-pointer" />
        <input
          type="text"
          placeholder="Name"
          className="h-[40px] w-full mt-[16px]"
        />
        <Button variant="contained" className="w-full">
          Create
        </Button>
      </div>
    </Dialog>
  );
};

export default NewBotModel;

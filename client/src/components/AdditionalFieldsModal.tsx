import { Dialog } from '@mui/material';
import { FuryData } from './FuryEngineNode';
import { GetFuryInput } from './GetFuryInput';
import SvgClose from './SvgComps/Close';
import { useUpdateNodeInternals } from 'reactflow';

export const AdditionalFieldsModal = ({
  data,
  onClose
}: {
  data: FuryData;
  onClose: () => void;
}) => {
  const updateNodeInternals = useUpdateNodeInternals();

  return (
    <>
      <Dialog
        open={true}
        onClose={() => {
          updateNodeInternals(data.id);
          onClose();
        }}
      >
        <div
          className={`prose-nbx relative  gap-[16px] p-[16px] flex flex-col justify-center items-center w-[500px]`}
        >
          <SvgClose
            onClick={onClose}
            className="stroke-light-neutral-grey-900 absolute right-[8px] top-[8px] scale-[1.2] cursor-pointer"
          />

          <div className="flex flex-col w-full">
            {data?.node?.fields?.map((field, key) => {
              return !field.required ? (
                <div key={key} className="flex flex-col gap-[8px] relative w-full">
                  <span className="medium400 text-light-neutral-grey-600 flex items-center gap-[4px] p-[8px]">
                    {typeof field?.type === 'string'
                      ? GetFuryInput(data, field?.name, field?.type, key)
                      : GetFuryInput(data, field?.name, field?.type?.[0]?.type, key)}
                    {/* {field?.placeholder} */}
                  </span>
                </div>
              ) : (
                <></>
              );
            })}
          </div>
        </div>
      </Dialog>
    </>
  );
};

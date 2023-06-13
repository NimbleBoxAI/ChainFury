import { NodeDataType } from '../constants';
import { useAuthStates } from '../redux/hooks/dispatchHooks';
import { Field, Output } from '../redux/slices/authSlice';
import { nodeColors } from '../utils';
import ParameterComponent from './ParameterComponent';
import SvgTrash from './SvgComps/Trash';

export const FuryEngineNode = ({
  data
}: {
  data: {
    deleteMe: () => void;
    id: string;
    type: string;

    node: {
      outputs: Output[];
      description: string;
      fields: Field[];
      fn?: {
        node_id: string;
        model: {
          collection_name: string;
          id: string;
          description: string;
          tags: string[];
          vars: any[];
        };
      };
    };
  };
}) => {
  const { auth } = useAuthStates();
  return (
    <div
      className={`w-[350px] overflow-hidden border border-light-neutral-grey-200 rounded-[4px] shadow-sm bg-light-system-bg-primary prose-nbx`}
    >
      <div className="flex flex-col">
        <div className="p-[8px] bg-light-system-bg-secondary medium350 flex justify-between items-center border-b">
          <span className="semiBold250 text-light-neutral-grey-500 ">{data?.id ?? ''}</span>
          <div
            className="cursor-pointer"
            onClick={() => {
              data?.deleteMe?.();
            }}
          >
            <SvgTrash className="stroke-light-neutral-grey-500" />
          </div>
        </div>

        <div className="w-full h-full p-[8px]">
          <div className="w-full text-gray-500 text-sm py-[4px]">{data.node?.description}</div>
          <div className="flex flex-col">
            {data?.node?.fields?.map((field, key) => {
              return (
                <div key={key} className="flex flex-col gap-[8px]">
                  <span className="medium400 text-light-neutral-grey-600 flex items-center gap-[4px] p-[8px]">
                    {field?.name}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
        <div className="py-[8px] flex flex-col gap-[8px]">
          <span className="medium400 text-light-neutral-grey-600 flex items-center gap-[4px] p-[8px]">
            Output
          </span>
          <div>
            {data?.node?.outputs?.map((output, key) => {
              return (
                <div
                  key={key}
                  className="bg-light-system-bg-primary rounded-md p-[4px] border-l-[2px] medium300"
                >
                  {output?.name}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

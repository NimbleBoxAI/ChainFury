import { Tooltip } from '@mui/material';
import { Handle, Position } from 'reactflow';
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
      className={`w-[350px] border border-light-neutral-grey-200 rounded-[4px] shadow-sm bg-light-system-bg-primary prose-nbx`}
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
                <div key={key} className="flex flex-col gap-[8px] relative">
                  <Tooltip title={' (required)'}>
                    <Handle
                      type={'target'}
                      // position={left ? Position.Left : Position.Right}
                      id={'input' + key}
                      isValidConnection={(connection) => {
                        // const sourceArr = connection?.sourceHandle?.split('|')?.filter((t) => t !== '') ?? [];
                        // const targetArr = connection?.targetHandle?.split('|')?.filter((t) => t !== '') ?? [];
                        // const hasCommonElement = sourceArr.some((item) => targetArr.includes(item));
                        // if (hasCommonElement) {
                        //   return true;
                        // }
                        // const hasCommonElement = connection?.source?.split('|')?.some((item)
                        console.log({ connection });
                        return true;
                      }}
                      className={
                        'p-[2px] rounded-[2px!important] border border-[#000!important] bg-[#fff!important]  dark:bg-dark-system-bg-primary bg-light-system-bg-primary  left-[-12px!important]'
                      }
                      position={Position.Left} // style={{
                      //   borderColor: color,
                      //   top: position
                      // }}
                    ></Handle>
                  </Tooltip>
                  <span className="medium400 text-light-neutral-grey-600 flex items-center gap-[4px] p-[8px]">
                    {field?.name}----
                    {typeof field?.type === 'string' ? field?.type : field?.type?.[0]?.type}---
                    {field?.placeholder}
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
              console.log(output);
              return (
                <div
                  key={key}
                  className="bg-light-system-bg-primary rounded-md p-[4px] border-l-[2px] medium300 relative"
                >
                  <Tooltip title={' (required)'}>
                    <Handle
                      type={'source'}
                      // position={left ? Position.Left : Position.Right}
                      id={'id' + key}
                      isValidConnection={(connection) => {
                        // const sourceArr = connection?.sourceHandle?.split('|')?.filter((t) => t !== '') ?? [];
                        // const targetArr = connection?.targetHandle?.split('|')?.filter((t) => t !== '') ?? [];
                        // const hasCommonElement = sourceArr.some((item) => targetArr.includes(item));
                        // if (hasCommonElement) {
                        //   return true;
                        // }
                        console.log({ connection });
                        return true;
                      }}
                      className={
                        'p-[2px] rounded-[2px!important] border border-[#000!important] bg-[#fff!important]  dark:bg-dark-system-bg-primary bg-light-system-bg-primary  right-[-4px!important]'
                      }
                      position={Position.Right} // style={{
                      //   borderColor: color,
                      //   top: position
                      // }}
                    ></Handle>
                  </Tooltip>
                  {output?.name}---
                  {typeof output?.type === 'string' ? output?.type : output?.type?.[0]?.type}---
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

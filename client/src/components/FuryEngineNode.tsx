import { Tooltip } from '@mui/material';
import { Handle, Position, useUpdateNodeInternals } from 'reactflow';
import { useAuthStates } from '../redux/hooks/dispatchHooks';
import { Field, Output } from '../redux/slices/authSlice';
import SvgTrash from './SvgComps/Trash';
import { useEffect, useRef, useState } from 'react';

interface FuryData {
  deleteMe: () => void;
  id: string;
  type: string;

  node: {
    name: string;
    outputs: Output[];
    description: string;
    fields: Field[];
    fn?: {
      node_id?: string;
      model_id?: string;
      model_params?: any;
      model?: {
        collection_name: string;
        id: string;
        description: string;
        tags: string[];
        vars: any[];
      };
    };
  };
}

export const FuryEngineNode = ({ data }: { data: FuryData }) => {
  const { auth } = useAuthStates();
  return (
    <div
      className={`w-[350px] border border-light-neutral-grey-200 rounded-[4px] shadow-sm bg-light-system-bg-primary prose-nbx`}
    >
      <div className="flex flex-col">
        <div className="p-[8px] bg-light-system-bg-secondary medium350 flex justify-between items-center border-b">
          <span className="semiBold250 text-light-neutral-grey-500 ">
            {(data?.node?.name || data?.id) ?? ''}
          </span>
          <div
            className="cursor-pointer"
            onClick={() => {
              console.log('delete me', data);
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
                        // const hasCommonElement = connection?.source?.split('|')?.some();
                        // console.log(connection);
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
                    {typeof field?.type === 'string'
                      ? GetFuryInput(data, field?.name, field?.type, key)
                      : GetFuryInput(data, field?.name, field?.type?.[0]?.type, key)}
                    {/* {field?.placeholder} */}
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
                  className="bg-light-system-bg-primary rounded-md p-[4px] medium300 relative text-right"
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
                        console.log(connection);
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
                  {output?.name}(
                  {typeof output?.type === 'string' ? output?.type : output?.type?.[0]?.type})
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

const GetFuryInput = (data: FuryData, name: string, type: string, index: number) => {
  const ref = useRef(null) as any;
  const updateNodeInternals = useUpdateNodeInternals();
  const [value, setValue] = useState(
    data.node?.fn?.model_params?.[name] ?? data.node.fields[index].placeholder
  );

  useEffect(() => {
    updateNodeInternals(data.id);
  }, [value]);

  return (
    <div ref={ref} className="flex flex-col gap-[2px] w-full">
      <span>{name}</span>
      {type === 'string' ? (
        <textarea
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            if (!data.node.fn && data.node) {
              data.node.fn = {
                model_params: {}
              };
            }
            if (data.node.fn && !data.node.fn.model_params) {
              data.node.fn.model_params = {};
            }
            if (data.node.fn) data.node.fn.model_params[name] = e.target.value;
            data.node.fields[index].placeholder = e.target.value;
          }}
          className="nodrag w-full"
          rows={1}
        />
      ) : type === 'object' ? (
        <textarea
          className="nodrag w-full"
          rows={3}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            if (typeof data.node.fields[index]?.type === 'string')
              data.node.fields[index].placeholder = e.target.value;
            else data.node.fields[index].placeholder = JSON.parse(e.target.value);
            updateNodeInternals(data.id);
          }}
        />
      ) : type === 'number' ? (
        <input
          value={value}
          onChange={(e) => {
            updateNodeInternals(data.id);
            if (!isNaN(Number(e.target.value)))
              data.node.fields[index].placeholder = e.target.value;
          }}
          className="nodrag w-full"
          type="number"
        />
      ) : type === 'boolean' ? (
        <div className="flex gap-[8px]">
          <div className="flex items-center gap-[4px]">
            <input type="radio" id="huey" name="drone" value="huey" />
            <label htmlFor="huey">True</label>
          </div>
          <div className="flex items-center gap-[4px]">
            <input type="radio" id="huey" name="drone" value="huey" />
            <label htmlFor="huey">False</label>
          </div>
        </div>
      ) : (
        ''
      )}
    </div>
  );
};

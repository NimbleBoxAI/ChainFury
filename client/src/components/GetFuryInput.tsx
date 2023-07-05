import { useRef, useState, useEffect } from 'react';
import { useUpdateNodeInternals } from 'reactflow';
import { FuryData } from './FuryEngineNode';
import { safeJsonParse } from '../utils';
import SvgExpand from './SvgComps/Expand';
import SvgClose from './SvgComps/Close';
import { Dialog } from '@mui/material';

export const GetFuryInput = (data: FuryData, name: string, type: string, index: number) => {
  const ref = useRef(null) as any;
  const updateNodeInternals = useUpdateNodeInternals();
  const [value, setValue] = useState(
    data.node?.fn?.model_params?.[name] ?? data.node.fields[index].placeholder
  );
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    updateNodeInternals(data.id);
  }, [value]);

  return (
    <div ref={ref} className="flex flex-col gap-[2px] w-full">
      <div className="w-full flex justify-between items-center">
        {name}
        {isExpanded ? (
          <ExpandedInputModal
            data={data}
            index={index}
            onClose={() => {
              setIsExpanded(false);
            }}
            value={value}
            setValue={setValue}
          />
        ) : (
          ''
        )}
        {type === 'object' || data.node?.fields[index]?.items?.[0]?.type === 'object' ? (
          <div
            className="cursor-pointer"
            onClick={() => {
              setIsExpanded(true);
            }}
          >
            <SvgExpand />
          </div>
        ) : (
          ''
        )}
      </div>
      {type === 'string' || data.node?.fields[index]?.items?.[0]?.type === 'string' ? (
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
      ) : type === 'object' || data.node?.fields[index]?.items?.[0]?.type === 'object' ? (
        <textarea
          className="nodrag w-full"
          rows={3}
          value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
          onChange={(e) => {
            setValue(e.target.value);
            if (data.node.fn && !data.node.fn.model_params) {
              data.node.fn.model_params = {};
            }
            if (data.node.fn) data.node.fn.model_params[name] = safeJsonParse(e.target.value);
            data.node.fields[index].placeholder = safeJsonParse(e.target.value);

            updateNodeInternals(data.id);
          }}
        />
      ) : type === 'number' || data.node?.fields[index]?.items?.[0]?.type === 'number' ? (
        <input
          value={value}
          onChange={(e) => {
            if (!isNaN(parseInt(e.target.value))) {
              setValue(e.target.value);
              if (data.node.fn && !data.node.fn.model_params) {
                data.node.fn.model_params = {};
              }
              if (data.node.fn) data.node.fn.model_params[name] = Number(e.target.value);
              data.node.fields[index].placeholder = e.target.value;
              updateNodeInternals(data.id);
            }
          }}
          className="nodrag w-full"
          type="number"
        />
      ) : type === 'boolean' || data.node?.fields[index]?.items?.[0]?.type === 'boolean' ? (
        <div className="flex gap-[8px]">
          <div className="flex items-center gap-[4px]">
            <input
              onChange={(e) => {
                setValue(e.target.value);
                if (data.node.fn && !data.node.fn.model_params) {
                  data.node.fn.model_params = {};
                }
                if (data.node.fn) data.node.fn.model_params[name] = true;
                data.node.fields[index].placeholder = 'true';
                updateNodeInternals(data.id);
              }}
              type="radio"
              id="huey"
              name="drone"
              value="huey"
            />
            <label htmlFor="huey">True</label>
          </div>
          <div className="flex items-center gap-[4px]">
            <input
              onChange={(e) => {
                setValue(e.target.value);
                if (data.node.fn && !data.node.fn.model_params) {
                  data.node.fn.model_params = {};
                }
                if (data.node.fn) data.node.fn.model_params[name] = false;
                data.node.fields[index].placeholder = 'false';
                updateNodeInternals(data.id);
              }}
              type="radio"
              id="huey"
              name="drone"
              value="huey"
            />
            <label htmlFor="huey">False</label>
          </div>
        </div>
      ) : (
        ''
      )}
    </div>
  );
};

const ExpandedInputModal = ({
  data,
  index,
  onClose,
  value,
  setValue
}: {
  data: FuryData;
  index: number;
  onClose: () => void;
  value: string;
  setValue: (value: string) => void;
}) => {
  const updateNodeInternals = useUpdateNodeInternals();

  return (
    <Dialog
      open={true}
      onClose={() => {
        updateNodeInternals(data.id);
        onClose();
      }}
    >
      <div className="bg-white rounded-lg p-[8px] min-w-[600px] relative">
        <div className="flex justify-between items-center">
          <div className="text-lg semiBold250">Edit {data.node.fields[index].name}</div>
          <SvgClose
            onClick={onClose}
            className="stroke-light-neutral-grey-900 absolute right-[8px] top-[8px] scale-[1.2] cursor-pointer"
          />
        </div>
        <textarea
          className="nodrag w-full h-[600px]"
          rows={3}
          value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
          onChange={(e) => {
            setValue(e.target.value);
            if (data.node.fn && !data.node.fn.model_params) {
              data.node.fn.model_params = {};
            }
            if (data.node.fn)
              data.node.fn.model_params[data.node.fields[index].name] = safeJsonParse(
                e.target.value
              );
            data.node.fields[index].placeholder = safeJsonParse(e.target.value);
            updateNodeInternals(data.id);
          }}
        />
      </div>
    </Dialog>
  );
};

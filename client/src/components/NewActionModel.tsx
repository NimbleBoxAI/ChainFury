import { Button, Dialog, MenuItem, Select } from '@mui/material';
import { useEffect, useState } from 'react';
import SvgClose from './SvgComps/Close';
import { AdditionalFieldType } from '../redux/slices/authSlice';
import SvgTrash from './SvgComps/Trash';
import { useAuthStates } from '../redux/hooks/dispatchHooks';
import { convertStringToJson } from '../utils';
import { useNewActionMutation } from '../redux/services/auth';

const availableFields = ['string', 'number', 'boolean', 'object'];
const locMap = {
  'openai-chat': ['choices', 0, 'message', 'content'],
  'openai-completion': ['choices', 0, 'text']
} as Record<string, any>;

const NewActionModel = ({ onClose, refresh }: { onClose: () => void; refresh: () => void }) => {
  const [actionName, setActionName] = useState('' as string);
  const [selectedModal, setSelectedModal] = useState('' as string);
  const [promptValue, setPromptValue] = useState('' as string);
  const [newAction] = useNewActionMutation();
  const [availableModals, setAvailableModals] = useState<
    {
      name: string;
      description: string;
      id: string;
    }[]
  >([]);
  const { auth } = useAuthStates();

  useEffect(() => {
    const temp = auth.furyComponents?.['models']?.components?.map((val) => ({
      id: val.id,
      name: val.collection_name,
      description: val.description
    })) as {
      name: string;
      description: string;
      id: string;
    }[];
    setAvailableModals(temp ?? []);
    setSelectedModal(temp?.[0]?.id ?? '');
  }, [auth.furyComponents]);

  useEffect(() => {
    if (selectedModal === 'openai-chat') {
      setPromptValue(`{
  "messages": [{
    "role": "user",
    "content": \`
Your prompt here

Give a polite professional reply to \\"Why did the {{ animal }} cross the road?\\"
  \`}]
}`);
    } else
      setPromptValue(`{
      "prompt":\`
       Your prompt here avoid using backticks
      \`
}`);
  }, [selectedModal]);

  const createFuryAction = () => {
    const functinVals = convertStringToJson(promptValue);
    if (!functinVals) return alert('Invalid JSON');

    newAction({
      name: actionName,
      description: '',
      tags: [],
      fn: {
        model_id: selectedModal,
        model_params: {
          model: selectedModal === 'openai-chat' ? 'gpt-3.5-turbo' : 'text-davinci-003'
        },
        fn: functinVals
      },
      outputs: [
        {
          type: 'string',
          name: 'string',
          loc: locMap?.[selectedModal]
        }
      ]
    })
      .unwrap()
      .then((res) => {
        refresh();
        onClose();
      })
      .catch((err) => {
        alert(err.data?.message ?? 'Something went wrong');
      });
  };

  return (
    <Dialog open={true} onClose={onClose}>
      <div
        className={`prose-nbx relative  gap-[16px] p-[16px] flex flex-col justify-center items-center w-[500px]`}
      >
        <SvgClose
          onClick={onClose}
          className="stroke-light-neutral-grey-900 absolute right-[8px] top-[8px] scale-[1.2] cursor-pointer"
        />
        <input
          onChange={(e) => {
            setActionName(e.target.value);
          }}
          value={actionName}
          type="text"
          placeholder="Action Name"
          className="h-[40px] w-full mt-[16px]"
        />
        {/* <div className="flex flex-col text-start w-full">
          <span className="semiBold200">inputs</span>

          <div className="flex flex-col gap-[2px]">
            {inputName?.map((val, index) => {
              return (
                <NewActionInput
                  key={index}
                  inputName={val}
                  OnRemove={() => {
                    const temp = [...inputName];
                    const tempDef = [...defaultValue];
                    const tempType = [...fieldType];
                    tempDef.splice(index, 1);
                    tempType.splice(index, 1);
                    temp.splice(index, 1);
                    setDefaultValue(tempDef);
                    setFieldType(tempType);
                    setinputName(temp);
                  }}
                  fieldType={fieldType[index]}
                  defaultValue={defaultValue[index]}
                  setinputName={(arg) => {
                    const temp = [...inputName];
                    temp[index] = arg;
                    setinputName(temp);
                  }}
                  setFieldType={(arg) => {
                    const temp = [...fieldType];
                    temp[index] = arg;
                    setFieldType(temp);
                  }}
                  setDefaultValue={(arg) => {
                    const temp = [...defaultValue];
                    temp[index] = arg;
                    setDefaultValue(temp);
                  }}
                />
              );
            })}
          </div>
          <div
            className="flex flex-col text-center items-center cursor-pointer my-[8px]"
            onClick={() => {
              setinputName([...inputName, '']);
              setFieldType([...fieldType, 'string']);
            }}
          >
            + New Field
          </div>
        </div> */}
        <div className="flex flex-col text-start w-full">
          <span className="semiBold200">model</span>
          <Select
            sx={{
              padding: '0px!important'
            }}
            value={selectedModal}
            onChange={(e) => setSelectedModal(e.target.value as string)}
            className="w-full h-[40px!important] rounded-md bg-light-neutral-grey-100 mt-[8px]"
          >
            {availableModals.map((val: { name: string; description: string; id: string }) =>
              locMap?.[val?.id] ? (
                <MenuItem key={val.id} value={val.id}>
                  {val.id}
                </MenuItem>
              ) : (
                ''
              )
            )}
          </Select>
          <textarea
            value={promptValue}
            onChange={(e) => setPromptValue(e.target.value)}
            className="w-full h-[100px] rounded-sm bg-light-neutral-grey-100 mt-[8px]"
          ></textarea>
        </div>
        <Button
          disabled={!actionName || !selectedModal}
          onClick={createFuryAction}
          variant="contained"
          className="w-full"
        >
          Create
        </Button>
      </div>
    </Dialog>
  );
};

export default NewActionModel;

const NewActionInput = ({
  inputName,
  fieldType,
  defaultValue,
  setinputName,
  setFieldType,
  setDefaultValue,
  OnRemove
}: {
  inputName: string;
  fieldType: AdditionalFieldType;
  defaultValue: string;
  setinputName: (arg: string) => void;
  setFieldType: (arg: AdditionalFieldType) => void;
  setDefaultValue: (arg: string) => void;
  OnRemove?: () => void;
}) => {
  return (
    <>
      <div className="flex justify-between mt-[16px] items-center">
        <input
          onChange={(e) => {
            setinputName(e.target.value);
          }}
          value={inputName}
          type="text"
          placeholder="Name"
          className="h-[40px] w-[150px]"
        />
        <Select
          sx={{
            padding: '0px!important'
          }}
          value={fieldType}
          onChange={(e) => setFieldType(e.target.value as AdditionalFieldType)}
          className="w-[120px!important] h-[40px!important] rounded-md bg-light-neutral-grey-100"
        >
          {availableFields.map((field) => (
            <MenuItem key={field} value={field}>
              {field}
            </MenuItem>
          ))}
        </Select>
        {fieldType !== 'boolean' ? (
          <input
            onChange={(e) => {
              if (fieldType === 'number' && isNaN(Number(e.target.value))) return;
              setDefaultValue(e.target.value);
            }}
            value={defaultValue}
            type={'text'}
            placeholder="Default Value"
            className="h-[40px] w-[150px] "
          />
        ) : (
          <Select
            sx={{
              padding: '0px!important'
            }}
            value={defaultValue}
            defaultValue="true"
            onChange={(e) => setDefaultValue(e.target.value)}
            className="w-[150px!important] h-[40px!important] rounded-md bg-light-neutral-grey-100"
          >
            <MenuItem key={'true'} value={'true'}>
              True
            </MenuItem>
            <MenuItem key={'false'} value={'false'}>
              False
            </MenuItem>
          </Select>
        )}
        <div
          onClick={() => {
            if (OnRemove) OnRemove();
          }}
        >
          <SvgTrash className="cursor-pointer stroke-light-critical-red-600" />
        </div>
      </div>
    </>
  );
};

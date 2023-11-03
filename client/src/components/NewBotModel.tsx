import { Button, Dialog } from '@mui/material';
import { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStates } from '../redux/hooks/dispatchHooks';

import SvgClose from './SvgComps/Close';
import { ChainFuryContext } from '../App';

import {
  useCreateChainMutation,
} from '../redux/services/auth';

const NewBotModel = ({ onClose }: { onClose: () => void }) => {
  const navigate = useNavigate();
  const [chainName, setChainName] = useState('');
  const [chainDescription, setChainDescription] = useState('');
  const { auth } = useAuthStates();
  const { engine, setEngine } = useContext(ChainFuryContext);
  const [createBot] = useCreateChainMutation();

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
            setChainName(e.target.value?.replace(' ', '-'));
          }}
          value={chainName}
          type="text"
          placeholder="Name"
          className="h-[40px] w-full mt-[16px]"
        />
        <input
          onChange={(e) => {
            setChainDescription(e.target.value ?? '');
          }}
          value={chainDescription}
          type="text"
          placeholder="Description"
          className="h-[100px] w-full mt-[16px]"
        />

        <Button
          disabled={chainName.length === 0}
          onClick={() => {
            createBot({
              name: chainName,
              description: chainDescription,
              engine: "fury",
              token: auth?.accessToken ?? "",
              nodes: null,
              edges: null,
            })
              .unwrap()
              ?.then((res) => {
                if (res?.id) {
                  navigate(`/ui/dashboard/?id=${res.id}`);
                }
                else {
                  alert('Error creating bot');
                }
              })
              .catch((err) => {
                console.log(err);
                alert('Error creating bot');
              });
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

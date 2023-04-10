import { Button, Dialog } from '@mui/material';
import { useState } from 'react';
import { useChangePasswordMutation } from '../redux/services/auth';
import SvgClose from './SvgComps/Close';

const ChangePassword = ({ onClose }: { onClose: () => void }) => {
  const [password, setPassword] = useState('');
  const [oldPassword, setOldPassword] = useState('');
  const [changePassword] = useChangePasswordMutation();

  const handlePasswordChange = () => {
    changePassword({
      old_password: oldPassword,
      new_password: password,
      token: localStorage.getItem('accessToken') ?? ''
    })
      .unwrap()
      .then((res) => {
        alert('Password changed successfully');
        onClose();
      })
      .catch(() => {
        alert('Unable to change password');
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
            setOldPassword(e.target.value);
          }}
          value={oldPassword}
          className="w-full h-[40px] mt-[32px]"
          placeholder="Old password"
          type={'password'}
        />{' '}
        <input
          onChange={(e) => {
            setPassword(e.target.value);
          }}
          value={password}
          className="w-full h-[40px]"
          placeholder="New Password"
          type={'password'}
        />
        <Button
          disabled={password.length < 6 || password === ''}
          onClick={() => {
            handlePasswordChange();
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

export default ChangePassword;

import { Button } from '@mui/material';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch } from '../../redux/hooks/store';
import { useLoginMutation } from '../../redux/services/auth';
import { setAccessToken } from '../../redux/slices/authSlice';

const Login = () => {
  const navigate = useNavigate();
  const [loginMutation] = useLoginMutation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const dispatch = useAppDispatch();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (localStorage.getItem('accessToken')) {
      navigate('/ui/dashboard');
    }
  }, []);

  const handleLogin = () => {
    setLoading(true);
    loginMutation({ username, password })
      .unwrap()
      .then((res) => {
        if (res?.token) {
          dispatch(
            setAccessToken({
              accessToken: res.token
            })
          );
          navigate('/ui/dashboard');
        } else {
          alert('Invalid Credentials');
        }
      })
      .catch(() => {
        alert('Invalid Credentials');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div
      className={`flex relative flex-col prose-nbx items-center justify-center h-screen w-full `}
    >
      <div className="w-full flex flex-col max-w-[500px] border border-light-neutral-grey-200 shadow-lg rounded-md p-[16px] gap-[8px]">
        <div className="mb-[8px] flex flex-col items-center text-center w-full">
          <div className="w-[64px] h-[64px] mb-[8px]">
            <img src="/chainfury.png" alt="logo" />
          </div>
          <span className="semiBold700 text-light-neutral-grey-700 ">Welcome to ChainFury</span>
        </div>

        <input
          onChange={(e) => {
            setUsername(e.target.value);
          }}
          value={username}
          className="w-full h-[40px]"
          placeholder="Username"
        />
        <Button
          onClick={handleLogin}
          disabled={username.length === 0 || password.length === 0 || loading}
          className="h-[40px] mt-[8px!important] block"
          variant="contained"
          color="primary"
        >
          {loading ? 'Please wait' : 'Continue'}
        </Button>
      </div>
      <div
        style={{
          transform: 'matrix(1, 0, 0, -1, 0, 0)',
          background:
            'conic-gradient(from 180deg at 50% 50%, rgba(169, 151, 239, 0.7) -93.79deg, #FFFFFF 0.33deg, #69F6FF 114.74deg, #45B1FF 193.8deg, rgba(169, 151, 239, 0.7) 266.21deg, #FFFFFF 360.33deg)'
        }}
        className="blur-[50px] absolute w-screen h-[240px] bottom-0 right-0 opacity-[0.3]"
      ></div>
    </div>
  );
};

export default Login;

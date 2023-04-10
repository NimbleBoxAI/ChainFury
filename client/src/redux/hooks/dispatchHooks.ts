import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { getAuthStates } from '../slices/authSlice';

//@@useAuthStates - hook to get auth states
export const useAuthStates = () => {
  const state = useSelector(getAuthStates);
  return useMemo(() => ({ auth: state }), [state]);
};

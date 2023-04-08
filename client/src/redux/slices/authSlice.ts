import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../store";

type AuthState = {
  count: number;
};

const slice = createSlice({
  name: "auth",
  initialState: {
    count: 0,
  } as AuthState,
  reducers: {
    setCount: (
      state,
      { payload: { count } }: PayloadAction<{ count: number }>
    ) => {
      state.count = count;
    },
  },
});

export const { setCount } = slice.actions;

export default slice.reducer;

export const getAuthStates = (state: RootState) => state.auth;

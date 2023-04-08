import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../store";

type AuthState = {
  accessToken: string;
};

const slice = createSlice({
  name: "auth",
  initialState: {
    accessToken: localStorage.getItem("accessToken") ?? "",
  } as AuthState,
  reducers: {
    setAccessToken: (
      state,
      { payload: { accessToken } }: PayloadAction<{ accessToken: string }>
    ) => {
      localStorage.setItem("accessToken", accessToken);
      state.accessToken = accessToken;
    },
  },
});

export const { setAccessToken } = slice.actions;

export default slice.reducer;

export const getAuthStates = (state: RootState) => state.auth;

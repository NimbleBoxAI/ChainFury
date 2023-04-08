import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { APIClassType } from "../../constants";
import { RootState } from "../store";

type AuthState = {
  accessToken: string;
  components: ComponentsInterface;
};

interface ComponentsInterface {
  [key: string]: Record<string, APIClassType>;
}

const slice = createSlice({
  name: "auth",
  initialState: {
    accessToken: localStorage.getItem("accessToken") ?? "",
    components: {},
  } as AuthState,
  reducers: {
    setAccessToken: (
      state,
      { payload: { accessToken } }: PayloadAction<{ accessToken: string }>
    ) => {
      localStorage.setItem("accessToken", accessToken);
      state.accessToken = accessToken;
    },
    setComponents: (
      state,
      {
        payload: { components },
      }: PayloadAction<{ components: ComponentsInterface }>
    ) => {
      state.components = components;
    },
  },
});

export const { setAccessToken, setComponents } = slice.actions;

export default slice.reducer;

export const getAuthStates = (state: RootState) => state.auth;

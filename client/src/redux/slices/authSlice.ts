import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { APIClassType } from "../../constants";
import { RootState } from "../store";

type AuthState = {
  accessToken: string;
  components: ComponentsInterface;
  typesMap: Record<string, string[]>;
};

interface ComponentsInterface {
  [key: string]: Record<string, APIClassType>;
}

const slice = createSlice({
  name: "auth",
  initialState: {
    accessToken: localStorage.getItem("accessToken") ?? "",
    components: {},
    typesMap: {},
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
      const typesMap = {} as Record<string, string[]>;
      Object.keys(components)?.forEach((componentKey) => {
        const component = components[componentKey];
        const baseClasses = [] as string[];
        Object.values(component).forEach((value) => {
          value?.base_classes?.forEach((baseClass) => {
            if (!baseClasses.includes(baseClass)) {
              baseClasses.push(baseClass);
            }
          });
        });
        typesMap[componentKey] = baseClasses;
      });
      state.typesMap = typesMap;
    },
  },
});

export const { setAccessToken, setComponents } = slice.actions;

export default slice.reducer;

export const getAuthStates = (state: RootState) => state.auth;

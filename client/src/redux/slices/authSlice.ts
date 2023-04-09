import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { APIClassType } from "../../constants";
import { RootState } from "../store";

interface ChatBots {
  created_by: string;
  id: string;
  name: string;
  dag: {
    edges: any;
    nodes: any;
  };
}

interface PromptsInterface {
  gpt_rating: number;
  id: string;
  chatbot_user_rating: number;
  time_taken: number;
  created_at: string;
  meta: any;
  chatbot_id: string;
  input_prompt: string;
  user_rating: number;
  response: string;
  session_id: string;
}

type AuthState = {
  accessToken: string;
  components: ComponentsInterface;
  typesMap: Record<string, string[]>;
  chatBots: Record<string, ChatBots>;
  selectedChatBot: ChatBots;
  prompts: Record<string, PromptsInterface[]>;
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
    chatBots: {},
    selectedChatBot: {} as ChatBots,
    prompts: {},
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
    setChatBots: (
      state,
      { payload: { chatBots } }: PayloadAction<{ chatBots: ChatBots[] }>
    ) => {
      const tempChatBots = {} as Record<string, ChatBots>;
      chatBots.forEach((chatBot) => {
        tempChatBots[chatBot.id] = chatBot;
      });
      state.chatBots = tempChatBots;
    },
    setSelectedChatBot: (
      state,
      { payload: { chatBot } }: PayloadAction<{ chatBot: ChatBots }>
    ) => {
      state.selectedChatBot = chatBot;
    },
    setPrompts: (
      state,
      {
        payload: { prompts, chatbot_id },
      }: PayloadAction<{ chatbot_id: string; prompts: PromptsInterface[] }>
    ) => {
      const tempList = JSON.parse(JSON.stringify(state?.prompts));
      if (!tempList[chatbot_id]) {
        tempList[chatbot_id] = prompts;
      }
      state.prompts = tempList;
    },
  },
});

export const {
  setAccessToken,
  setComponents,
  setChatBots,
  setSelectedChatBot,
  setPrompts,
} = slice.actions;

export default slice.reducer;

export const getAuthStates = (state: RootState) => state.auth;

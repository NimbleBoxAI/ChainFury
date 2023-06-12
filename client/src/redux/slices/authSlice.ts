import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { APIClassType } from '../../constants';
import { RootState } from '../store';

interface ChatBots {
  created_by: string;
  id: string;
  name: string;
  description?: string;
  dag: {
    edges: any;
    nodes: any;
  };
}

interface PromptsInterface {
  num_tokens: string;
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

export interface MetricsInterface {
  total_conversations: number;
  total_tokens_processed: number;
  no_of_conversations_rated_by_developer: number;
  no_of_conversations_rated_by_end_user: number;
  no_of_conversations_rated_by_openai: number;
  average_rating: number;
  average_chatbot_user_ratings: number;
  average_developer_ratings: number;
  average_openai_ratings: number;
}

export interface FuryComponentInterface {
  id: string;
  type: string;
  fn?: {
    node_id: string;
    model: {
      collection_name: string;
      id: string;
      description: string;
      tags: string[];
      vars: any[];
    };
  };
  description: string;
  fields: Field[];
  outputs: Output[];
}

interface Field {
  type: FieldType;
  required?: boolean;
  show?: boolean;
  name: string;
  placeholder?: string;
  items?: Item[];
  additionalProperties?: {
    type: FieldType;
  };
}

interface Item {
  type: FieldType;
}

type FieldType = 'string' | 'number' | 'boolean' | 'array' | 'object';

interface Output {
  type: FieldType;
  name: string;
  loc?: string[];
}

type AuthState = {
  accessToken: string;
  components: ComponentsInterface;
  furyComponents: Record<string, { type: string; components: FuryComponentInterface[] }>;
  typesMap: Record<string, string[]>;
  chatBots: Record<string, ChatBots>;
  selectedChatBot: ChatBots;
  prompts: Record<string, PromptsInterface[]>;
  templates: Record<string, ChatBots>;
  metrics: Record<string, MetricsInterface>;
};

interface ComponentsInterface {
  [key: string]: Record<string, APIClassType>;
}

const slice = createSlice({
  name: 'auth',
  initialState: {
    accessToken: localStorage.getItem('accessToken') ?? '',
    components: {},
    furyComponents: {},
    typesMap: {},
    chatBots: {},
    selectedChatBot: {} as ChatBots,
    prompts: {},
    templates: {},
    metrics: {}
  } as AuthState,
  reducers: {
    setAccessToken: (
      state,
      { payload: { accessToken } }: PayloadAction<{ accessToken: string }>
    ) => {
      localStorage.setItem('accessToken', accessToken);
      state.accessToken = accessToken;
    },
    setComponents: (
      state,
      { payload: { components } }: PayloadAction<{ components: ComponentsInterface }>
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
    setFuryComponents: (
      state,
      { payload: { furyComponents } }: PayloadAction<{ furyComponents: any }>
    ) => {
      state.furyComponents = furyComponents;
    },
    setChatBots: (state, { payload: { chatBots } }: PayloadAction<{ chatBots: ChatBots[] }>) => {
      const tempChatBots = {} as Record<string, ChatBots>;
      chatBots.forEach((chatBot) => {
        tempChatBots[chatBot.id] = chatBot;
      });
      state.chatBots = tempChatBots;
    },
    setTemplates: (state, { payload: { templates } }: PayloadAction<{ templates: ChatBots[] }>) => {
      const tempTemplates = {} as Record<string, ChatBots>;
      templates.forEach((template) => {
        tempTemplates[template.id] = template;
      });
      state.templates = tempTemplates;
    },
    setSelectedChatBot: (state, { payload: { chatBot } }: PayloadAction<{ chatBot: ChatBots }>) => {
      state.selectedChatBot = chatBot;
    },
    setPrompts: (
      state,
      {
        payload: { prompts, chatbot_id }
      }: PayloadAction<{ chatbot_id: string; prompts: PromptsInterface[] }>
    ) => {
      const tempList = JSON.parse(JSON.stringify(state?.prompts));
      if (!tempList[chatbot_id]) {
        tempList[chatbot_id] = prompts;
      }
      state.prompts = tempList;
    },
    setMetrics: (state, { payload: { data } }: PayloadAction<{ data: any[] }>) => {
      const tempMetrics = {} as any;
      data?.forEach((item) => {
        const entries = Object.entries(item);
        tempMetrics[entries[0][0]] = entries[0][1];
      });
      state.metrics = tempMetrics;
    }
  }
});

export const {
  setAccessToken,
  setComponents,
  setChatBots,
  setSelectedChatBot,
  setPrompts,
  setTemplates,
  setMetrics,
  setFuryComponents
} = slice.actions;

export default slice.reducer;

export const getAuthStates = (state: RootState) => state.auth;

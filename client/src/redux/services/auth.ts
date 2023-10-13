import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { BASE_URL, DEFAULT_RESPONSE } from '../../constants';
import { RootState } from '../store';

interface LoginRequest {
  username: string;
  password: string;
}

let token: string | null = null;
export const authApi = createApi({
  baseQuery: fetchBaseQuery({
    prepareHeaders: (headers, { getState }) => {
      // By default, if we have a token in the store, let's use that for authenticated requests
      token = (getState() as RootState)?.auth?.accessToken;
      headers.set('content-type', 'application/json;charset=UTF-8');
      if (token) {
        headers.set('token', `${token}`);
      }
      return headers;
    },
    credentials: 'omit'
  }),
  endpoints: (builder) => ({

    // TODO: this is deprecated API, remove this
    components: builder.mutation<DEFAULT_RESPONSE, void>({
      query: () => ({
        url: `${BASE_URL}/api/v1/flow/components`,
        method: 'GET'
      })
    }),
    getTemplates: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
      }
    >({
      query: () => ({
        url: `${BASE_URL}/api/v1/template/`,
        method: 'GET'
      })
    }),
    addUserFeedBack: builder.mutation<
      DEFAULT_RESPONSE,
      {
        score: number;
        prompt_id: string;
      }
    >({
      query: ({ score, prompt_id }) => ({
        url: `${BASE_URL}/api/v1/prompts/${prompt_id}/feedback`,
        method: 'PUT',
        body: {
          score
        }
      })
    }),

    // fury Action APIs
    furyComponents: builder.mutation<DEFAULT_RESPONSE, void>({
      query: () => ({
        url: `${BASE_URL}/api/v1/fury/`,
        method: 'GET'
      })
    }),
    furyComponentDetails: builder.mutation<
      DEFAULT_RESPONSE,
      {
        component_type: string;
      }
    >({
      query: ({ component_type }) => ({
        url: `${BASE_URL}/api/v1/fury/components/${component_type}`,
        method: 'GET'
      })
    }),
    newAction: builder.mutation<
      DEFAULT_RESPONSE,
      {
        name: string;
        description: string;
        tags: [];
        fn: {
          model_id: string;
          model_params: {};
          fn: {};
        };
        outputs: [
          {
            type: string;
            name: string;
            loc: string;
          }
        ];
      }
    >({
      query: (credentials) => ({
        url: `${BASE_URL}/api/v1/fury/actions/`,
        method: 'POST',
        body: credentials
      })
    }),
    getActions: builder.mutation<DEFAULT_RESPONSE, {}>({
      query: () => ({
        url: `${BASE_URL}/api/v1/fury/actions/`,
        method: 'GET'
      })
    }),

    /*

    Migrated to newer APIs

    */

    getMetrics: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
        chain_id: string;
      }
    >({
      query: ({ chain_id }) => ({
        url: `${BASE_URL}/api/v2/chains/${chain_id}/metrics/`,
        method: 'GET'
      })
    }),

    addInternalFeedBack: builder.mutation<
      DEFAULT_RESPONSE,
      {
        score: number;
        prompt_id: string;
        chatbot_id: string;
      }
    >({
      query: ({ score, prompt_id, chatbot_id }) => ({
        url: `${BASE_URL}/api/v2/prompts/${prompt_id}/feedback`,
        method: 'PUT',
        body: {
          score
        }
      })
    }),

    login: builder.mutation<DEFAULT_RESPONSE, LoginRequest>({
      query: (credentials) => ({
        url: `${BASE_URL}/user/login/`,
        method: 'POST',
        body: credentials
      })
    }),

    signup: builder.mutation<
      DEFAULT_RESPONSE,
      {
        username: string;
        email: string;
        password: string;
      }
    >({
      query: (credentials) => ({
        url: `${BASE_URL}/user/signup/`,
        method: 'POST',
        body: credentials
      })
    }),

    changePassword: builder.mutation<
      DEFAULT_RESPONSE,
      {
        old_password: string;
        new_password: string;
      }
    >({
      query: (credentials) => ({
        url: `${BASE_URL}/user/change_password/`,
        method: 'POST',
        body: {
          old_password: credentials.old_password,
          new_password: credentials.new_password,
          username: ''
        }
      })
    }),

    // get prompts
    getPrompts: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
        id: string;
      }
    >({
      query: (credentials) => ({
        url: `${BASE_URL}/api/v2/prompts/?chatbot_id=${credentials?.id}&limit=50&offset=0`,
        method: 'GET'
      })
    }),

    // get specific prompt
    getSteps: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
        id: string;
        prompt_id: string;
      }
    >({
      query: ({ id, prompt_id }) => ({
        url: `${BASE_URL}/api/v2/prompts/${prompt_id}/`,
        method: 'GET'
      })
    }),

    // delete prompt
    deletePrompt: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
        prompt_id: string;
      }
    >({
      query: ({ prompt_id }) => ({
        url: `${BASE_URL}/api/v2/prompts/${prompt_id}/`,
        method: 'DELETE'
      })
    }),

    // list chains API
    getBots: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
      }
    >({
      query: (credentials) => ({
        url: `${BASE_URL}/api/v2/chains/`,
        method: 'GET'
      })
    }),

    // create chain API
    createBot: builder.mutation<
      DEFAULT_RESPONSE,
      {
        name: string;
        nodes: any;
        edges: any;
        token: string;
        engine: string;
        sample?: Record<string, any>;
        main_in?: string;
        main_out?: string;
      }
    >({
      query: (credentials) => ({
        url: `${BASE_URL}/api/v2/chains/`,
        method: 'POST',
        body: {
          engine: credentials.engine,
          name: credentials.name,
          dag: {
            nodes: credentials.nodes ?? [],
            edges: credentials.edges ?? [],
            sample: credentials.sample ?? undefined,
            main_in: credentials.main_in ?? undefined,
            main_out: credentials.main_out ?? undefined
          }
        }
      })
    }),

    // edit chain API
    editBot: builder.mutation<
      DEFAULT_RESPONSE,
      {
        name: string;
        nodes: any;
        edges: any;
        token: string;
        id: string;
        engine: string;
        sample?: Record<string, any>;
        main_in?: string;
        main_out?: string;
      }
    >({
      query: (credentials) => ({
        url: `${BASE_URL}/api/v2/chains/${credentials?.id}`,
        method: 'PUT',
        body: {
          name: credentials.name,
          dag: {
            nodes: credentials.nodes ?? [],
            edges: credentials.edges ?? [],
            sample: credentials.sample ?? undefined,
            main_in: credentials.main_in ?? undefined,
            main_out: credentials.main_out ?? undefined
          },
          engine: credentials.engine,
          update_keys: ['dag']
        }
      })
    }),

    // run chain
    processPrompt: builder.mutation<
      DEFAULT_RESPONSE,
      {
        chatbot_id: string;
        chat_history: string[];
        session_id: string;
        new_message: string;
      }
    >({
      query: ({
        chatbot_id,
        chat_history,
        session_id,
        new_message
      }: {
        chatbot_id: string;
        chat_history: string[];
        session_id: string;
        new_message: string;
      }) => (
        console.log('chatbot_id', chatbot_id),
        {
          url: `${BASE_URL}/api/v2/chains/${chatbot_id}/`,
          method: 'POST',
          body: {
            chat_history,
            session_id,
            new_message
          }
        })
    }),

  })
});

export const {
  useLoginMutation,
  useSignupMutation,
  useComponentsMutation,
  useGetMetricsMutation,
  useAddUserFeedBackMutation,
  useAddInternalFeedBackMutation,
  useGetTemplatesMutation,
  useChangePasswordMutation,
  // useGetAllBotMetricsMutation,
  useFuryComponentsMutation,
  useFuryComponentDetailsMutation,
  useNewActionMutation,
  useGetActionsMutation,



  useGetPromptsMutation,
  useGetStepsMutation,
  useDeletePromptMutation,
  useGetBotsMutation,
  useCreateBotMutation,
  useEditBotMutation,
  useProcessPromptMutation,
} = authApi;

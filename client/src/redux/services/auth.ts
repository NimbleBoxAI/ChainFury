import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { BASE_URL, DEFAULT_RESPONSE } from "../../constants";
import { RootState } from "../store";

interface LoginRequest {
  username: string;
  password: string;
}

let token: string | null = null;
export const authApi = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: `${BASE_URL}/`,
    prepareHeaders: (headers, { getState }) => {
      // By default, if we have a token in the store, let's use that for authenticated requests
      token = (getState() as RootState)?.auth?.accessToken;
      headers.set("content-type", "application/json;charset=UTF-8");
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
    credentials: "include",
  }),
  endpoints: (builder) => ({
    login: builder.mutation<DEFAULT_RESPONSE, LoginRequest>({
      query: (credentials) => ({
        url: "/login",
        method: "POST",
        body: credentials,
      }),
    }),
    components: builder.mutation<DEFAULT_RESPONSE, void>({
      query: () => ({
        url: "/flow/components",
        method: "GET",
      }),
    }),
    getPrompts: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
        id: string;
      }
    >({
      query: (credentials) => ({
        url: `/chatbot/${credentials?.id}/prompts?token=` + credentials?.token,
        method: "GET",
      }),
    }),
    getBots: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
      }
    >({
      query: (credentials) => ({
        url: "/chatbot/?token=" + credentials?.token,
        method: "GET",
      }),
    }),
    getSteps: builder.mutation<
      DEFAULT_RESPONSE,
      {
        token: string;
        id: string;
        prompt_id: string;
      }
    >({
      query: ({ token, id, prompt_id }) => ({
        url:
          `/chatbot/${id}/prompt/${prompt_id}/intermediate_steps?token=` +
          token,
        method: "GET",
      }),
    }),
    createBot: builder.mutation<
      DEFAULT_RESPONSE,
      {
        name: string;
        nodes: any;
        edges: any;
        token: string;
      }
    >({
      query: (credentials) => ({
        url: "/chatbot/?token=" + token,
        method: "POST",
        body: {
          name: credentials.name,
          dag: {
            nodes: credentials.nodes,
            edges: credentials.edges,
          },
        },
      }),
    }),
    editBot: builder.mutation<
      DEFAULT_RESPONSE,
      {
        name: string;
        nodes: any;
        edges: any;
        token: string;
        id: string;
      }
    >({
      query: (credentials) => ({
        url: `/chatbot/${credentials?.id}?token=` + token,
        method: "PUT",
        body: {
          name: credentials.name,
          dag: {
            nodes: credentials.nodes,
            edges: credentials.edges,
          },
        },
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useComponentsMutation,
  useCreateBotMutation,
  useGetBotsMutation,
  useEditBotMutation,
  useGetPromptsMutation,
  useGetStepsMutation,
} = authApi;

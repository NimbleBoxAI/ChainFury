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
  }),
});

export const { useLoginMutation, useComponentsMutation } = authApi;

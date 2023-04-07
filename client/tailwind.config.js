/** @type {import('tailwindcss').Config} */
export default {
  darkMode: false,
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: [
          "-apple-system",
          "BlinkMacSystemFont",
          "'Segoe UI'",
          "Roboto",
          "Oxygen",
          "Ubuntu",
          "'Fira Sans'",
          "'Droid Sans'",
          "'Helvetica Neue'",
          "sans-serif",
        ],
        body: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "Liberation Mono",
          "Courier New",
          "monospace",
        ],
      },
      typography: (theme) => ({
        nbx: {
          css: [
            {
              ".bold900,.bold850,.bold800,.bold750,.bold700,.bold650,.bold600,.bold550,.bold500,.bold450,.bold400,.bold350,.bold300,.bold250,.bold200,.bold150,.bold100,.bold50":
                {
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: "700!important",
                },
              ".semiBold900,.semiBold850, .semiBold800,.semiBold750, .semiBold700 ,.semiBold650,.semiBold600,.semiBold550, .semiBold500,.semiBold450, .semiBold400,.semiBold350, .semiBold300,.semiBold250,.semiBold200,.semiBold150,.semiBold100":
                {
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: "600!important",
                },
              ".medium900,.medium850, .medium800,.medium750, .medium700 ,.medium650,.medium600,.medium550, .medium500,.medium450, .medium400,.medium350, .medium300,.medium250 ,.medium200,.medium150 ,.medium100":
                {
                  fontFamily: "'Inter', sans-serif!important",
                  fontWeight: "500!important",
                },
              ".regular900,.regular850 ,.regular800,.regular750, .regular700 ,.regular650,.regular600,.regular550, .regular500,.regular450, .regular400,.regular350, .regular300,.regular250,.regular200,.regular150,.regular100":
                {
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: "400!important",
                },
              ".bold900": {
                fontSize: "40px",
                lineHeight: "48px",
              },
              ".bold800": {
                fontSize: "32px",
                lineHeight: "40px",
              },
              ".bold700": {
                fontSize: "24px",
                lineHeight: "32px",
              },
              ".bold600": {
                fontSize: "20px",
                lineHeight: "28px",
              },
              ".bold500": {
                fontSize: "18px",
                lineHeight: "24px",
              },
              ".bold400": {
                fontSize: "16px",
                lineHeight: "24px",
              },
              ".bold300": {
                fontSize: "14px",
                lineHeight: "20px",
              },
              ".bold250": {
                fontSize: "13px",
                lineHeight: "18px",
              },
              ".bold200": {
                fontSize: "12px",
                lineHeight: "16px",
              },
              ".bold150": {
                fontSize: "11px",
                lineHeight: "16px",
              },
              ".bold100": {
                fontSize: "10px",
                lineHeight: "14px",
              },
              //Semi bold
              ".semiBold900": {
                fontSize: "40px",
                lineHeight: "48px",
              },
              ".semiBold800": {
                fontSize: "32px",
                lineHeight: "40px",
              },
              ".semiBold700": {
                fontSize: "24px",
                lineHeight: "32px",
              },
              ".semiBold600": {
                fontSize: "20px",
                lineHeight: "28px",
              },
              ".semiBold500": {
                fontSize: "18px",
                lineHeight: "24px",
              },
              ".semiBold400": {
                fontSize: "16px",
                lineHeight: "24px",
              },
              ".semiBold300": {
                fontSize: "14px",
                lineHeight: "20px",
              },
              ".semiBold250": {
                fontSize: "13px",
                lineHeight: "18px",
              },
              ".semiBold200": {
                fontSize: "12px",
                lineHeight: "16px",
              },
              ".semiBold150": {
                fontSize: "11px",
                lineHeight: "16px",
              },
              ".semiBold100": {
                fontSize: "10px",
                lineHeight: "14px",
              },
              //Medium
              ".medium900": {
                fontSize: "40px",
                lineHeight: "48px",
              },
              ".medium800": {
                fontSize: "32px",
                lineHeight: "40px",
              },
              ".medium700": {
                fontSize: "24px",
                lineHeight: "32px",
              },
              ".medium600": {
                fontSize: "20px",
                lineHeight: "28px",
              },
              ".medium500": {
                fontSize: "18px",
                lineHeight: "24px",
              },
              ".medium400": {
                fontSize: "16px",
                lineHeight: "24px",
              },
              ".medium300": {
                fontSize: "14px",
                lineHeight: "20px",
              },
              ".medium250": {
                fontSize: "13px!important",
                lineHeight: "18px!important",
              },
              ".medium200": {
                fontSize: "12px!important",
                lineHeight: "16px!important",
              },
              ".medium150": {
                fontSize: "11px!important",
                lineHeight: "16px!important",
              },
              ".medium100": {
                fontSize: "10px",
                lineHeight: "14px",
              },
              //Regular
              ".regular900": {
                fontSize: "40px",
                lineHeight: "48px",
              },
              ".regular800": {
                fontSize: "32px",
                lineHeight: "40px",
              },
              ".regular700": {
                fontSize: "24px",
                lineHeight: "32px",
              },
              ".regular600": {
                fontSize: "20px",
                lineHeight: "28px",
              },
              ".regular500": {
                fontSize: "18px",
                lineHeight: "24px",
              },
              ".regular400": {
                fontSize: "16px",
                lineHeight: "24px",
              },
              ".regular300": {
                fontSize: "14px",
                lineHeight: "20px",
              },
              ".regular250": {
                fontSize: "13px",
                lineHeight: "18px",
              },
              ".regular200": {
                fontSize: "12px",
                lineHeight: "16px",
              },
              ".regular150": {
                fontSize: "11px",
                lineHeight: "16px",
              },
              ".regular100": {
                fontSize: "10px",
                lineHeight: "14px",
              },
              ".code400": {
                fontFamily: "'Roboto Mono', sans-serif",
                fontWeight: 400,
                fontSize: "16px",
                lineHeight: "24px",
              },
              ".code300": {
                fontFamily: "'Roboto Mono', sans-serif",
                fontWeight: 400,
                fontSize: "14px",
                lineHeight: "20px",
              },
            },
          ],
        },
      }),
      colors: {
        nbxBlue: "#0879FF",
        light: {
          system: {
            "bg-primary": "#FFFFFF",
            "bg-secondary": "#F6F8FC",
            header: "#161B22",
          },
          primary: {
            "blue-800": "#004BA3",
            "blue-600": "#006EF5",
            "blue-400": "#4DA1FF",
            "blue-200": "#B1DAFF",
            "blue-50": "#DFF0FF",
          },
          neutral: {
            "grey-900": "#0F1A2A!important",
            "grey-800": "#1E2A3B",
            "grey-700": "#27364B",
            "grey-600": "#475569",
            "grey-500": "#64748B",
            "grey-400": "#94A3B8!important",
            "grey-300": "#CBD4E1",
            "grey-200": "#E2E8F0",
            "grey-100": "#F1F4F9",
            "grey-50": "#F6F8FC",
            "white-900": "#FFFFFF",
          },
          success: {
            "green-800": "#003D2C",
            "green-600": "#007F5F",
            "green-400": "#95C9B4",
            "green-50": "#F1F8F5",
          },
          warning: {
            "yellow-800": "#916A00",
            "yellow-600": "#B98900",
            "yellow-500": "#EAB308",
            "yellow-400": "#E1B878",
            "yellow-50": "#FFF5EA",
          },
          critical: {
            "red-800": "#6C0F00",
            "red-600": "#CC3340",
            "red-400": "#E0B3B2",
            "red-50": "#FFE9E8",
          },
          violet: {
            400: "#8F6BF2",
          },
          orange: {
            400: "#FB923C",
          },
          teal: {
            500: "#14A88F",
            600: "#0D9488",
          },
        },
        dark: {
          system: {
            "bg-primary": "#0E1116",
            "bg-secondary": "#090D11",
            header: "#161B22",
          },
          primary: {
            "blue-800": "#94C5FF",
            "blue-600": "#4D9DFF",
            "blue-400": "#0067DB",
            "blue-200": "#004280",
            "blue-50": "#0E386A",
          },
          neutral: {
            "grey-900": "#F0F6FC!important",
            "grey-800": "#C9D1D9",
            "grey-700": "#B1BAC4",
            "grey-600": "#8B949E",
            "grey-500": "#6E7681",
            "grey-400": "#484F58!important",
            "grey-300": "#30363D",
            "grey-200": "#21262D",
            "grey-100": "#161B22",
            "grey-50": "#0D1117",
            "white-900": "#FFFFFF",
          },
          success: {
            "green-800": "#17D6A0",
            "green-600": "#17D6A0",
            "green-400": "#32624F",
            "green-50": "#0A211F",
          },
          warning: {
            "yellow-800": "#FDCE48",
            "yellow-600": "#FDCE48",
            "yellow-400": "#75511A",
            "yellow-50": "#29281B",
          },
          critical: {
            "red-800": "#D55862",
            "red-600": "#D55862",
            "red-400": "#893230",
            "red-50": "#1D1419",
          },
          teal: {
            500: "#14A88F",
            600: "#0D9488",
          },
        },
        violet: {
          400: "#8F6BF2",
        },
        orange: {
          400: "#FB923C",
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

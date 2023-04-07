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
    },
  },
  plugins: [],
};

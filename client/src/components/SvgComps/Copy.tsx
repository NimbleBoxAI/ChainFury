import * as React from "react";

const SvgCopy = (props: { className?: string }) => (
  <svg
    width={20}
    height={20}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <path
      d="M15 5.833H8.333c-.92 0-1.666.746-1.666 1.667v8.333c0 .92.746 1.667 1.666 1.667H15c.92 0 1.667-.746 1.667-1.667V7.5c0-.92-.747-1.667-1.667-1.667Z"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M13.333 5.833V4.167A1.667 1.667 0 0 0 11.667 2.5H5a1.667 1.667 0 0 0-1.667 1.667V12.5A1.667 1.667 0 0 0 5 14.167h1.667"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export default SvgCopy;

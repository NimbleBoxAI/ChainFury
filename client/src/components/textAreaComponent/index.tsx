import { useEffect, useState } from "react";
import { TextAreaComponentType } from "../../constants";

export default function TextAreaComponent({
  value,
  onChange,
  disabled,
}: TextAreaComponentType) {
  const [myValue, setMyValue] = useState(value);
  useEffect(() => {
    if (disabled) {
      setMyValue("");
      onChange("");
    }
  }, [disabled, onChange]);
  return (
    <div className={disabled ? "pointer-events-none cursor-not-allowed" : ""}>
      <div className="w-full flex items-center gap-3">
        <span
          className={
            "truncate block w-full text-gray-500 px-3 py-2 rounded-md border border-gray-300 dark:border-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" +
            (disabled ? " bg-gray-200" : "")
          }
        >
          {myValue !== "" ? myValue : "Text empty"}
        </span>
        <input
          className="nodrag w-full h-[28px]"
          value={myValue}
          onChange={(e) => {
            setMyValue(e?.target?.value);
            onChange(e?.target?.value);
          }}
        />
      </div>
    </div>
  );
}

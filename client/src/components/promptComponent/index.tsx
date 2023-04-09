import { useContext, useEffect, useState } from "react";
import { TextAreaComponentType } from "../../constants";

export default function PromptAreaComponent({
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
    <div
      className={
        disabled ? "pointer-events-none cursor-not-allowed w-full" : " w-full"
      }
    >
      <div className="w-full flex items-center gap-3">
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

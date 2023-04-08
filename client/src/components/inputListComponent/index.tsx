import { useEffect, useState } from "react";
import { InputListComponentType } from "../../constants";

export default function InputListComponent({
  value,
  onChange,
  disabled,
}: InputListComponentType) {
  const [inputList, setInputList] = useState(value ?? [""]);
  useEffect(() => {
    if (disabled) {
      setInputList([""]);
      onChange([""]);
    }
  }, [disabled, onChange]);
  return (
    <div
      className={
        (disabled ? "pointer-events-none cursor-not-allowed" : "") +
        "flex flex-col gap-3"
      }
    >
      {inputList.map((i: any, idx: number) => (
        <div key={idx} className="w-full flex gap-3">
          <input
            type="text"
            value={i}
            className={
              "block w-full form-input rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" +
              (disabled ? " bg-gray-200" : "")
            }
            placeholder="Type a text"
            onChange={(e) => {
              setInputList((old: any) => {
                let newInputList = JSON.parse(JSON.stringify(old));
                newInputList[idx] = e.target.value;
                return newInputList;
              });
              onChange(inputList);
            }}
          />
          {idx === inputList.length - 1 ? (
            <button
              onClick={() => {
                setInputList((old) => {
                  let newInputList = JSON.parse(JSON.stringify(old));
                  newInputList.push("");
                  return newInputList;
                });
                onChange(inputList);
              }}
            >
              +
            </button>
          ) : (
            <button
              onClick={() => {
                setInputList((old: any) => {
                  let newInputList = JSON.parse(JSON.stringify(old));
                  newInputList.splice(idx, 1);
                  return newInputList;
                });
                onChange(inputList);
              }}
            >
              X
            </button>
          )}
        </div>
      ))}
    </div>
  );
}

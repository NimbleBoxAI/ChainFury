import { Tooltip } from "@mui/material";
import { useRef, useState, useEffect } from "react";
import { useUpdateNodeInternals, Handle, Position } from "reactflow";
import { ParameterComponentType } from "../constants";
import CodeAreaComponent from "./codeAreaComponent";
import Dropdown from "./dropdownComponent";
import FloatComponent from "./floatComponent";
import InputComponent from "./inputComponent";
import InputFileComponent from "./inputFileComponent";
import InputListComponent from "./inputListComponent";
import IntComponent from "./intComponent";
import PromptAreaComponent from "./promptComponent";
import TextAreaComponent from "./textAreaComponent";
import ToggleComponent from "./toggleComponent";

export default function ParameterComponent({
  left,
  id,
  data,
  tooltipTitle,
  title,
  color,
  type,
  name = "",
  required = false,
}: ParameterComponentType) {
  const ref = useRef(null) as any;
  const updateNodeInternals = useUpdateNodeInternals();
  const [position, setPosition] = useState(0);

  useEffect(() => {
    if (ref.current && ref?.current?.offsetTop && ref.current?.clientHeight) {
      setPosition(ref.current.offsetTop + ref.current.clientHeight / 2);
      updateNodeInternals(data.id);
    }
  }, [data.id, ref, updateNodeInternals]);

  useEffect(() => {
    updateNodeInternals(data.id);
  }, [data.id, position, updateNodeInternals]);

  const [enabled, setEnabled] = useState(
    data?.node?.template[name]?.value ?? false
  );

  return (
    <div
      ref={ref}
      className="w-full flex flex-wrap justify-between items-center bg-gray-50 dark:bg-gray-800 dark:text-white font-sans"
    >
      <>
        <div
          className={
            " text-sm capitalize truncate w-full " +
            (left ? "" : "text-end pr-[8px]")
          }
        >
          {title}
          <span className="text-red-600">{required ? " *" : ""}</span>
        </div>
        {left &&
        (type === "str" ||
          type === "bool" ||
          type === "float" ||
          type === "code" ||
          type === "prompt" ||
          type === "file" ||
          type === "int") ? (
          <></>
        ) : (
          <Tooltip title={tooltipTitle + (required ? " (required)" : "")}>
            <Handle
              type={left ? "target" : "source"}
              position={left ? Position.Left : Position.Right}
              id={id}
              isValidConnection={(connection) => {
                const sourceArr =
                  connection?.sourceHandle
                    ?.split("|")
                    ?.filter((t) => t !== "") ?? [];
                const targetArr =
                  connection?.targetHandle
                    ?.split("|")
                    ?.filter((t) => t !== "") ?? [];
                const hasCommonElement = sourceArr.some((item) =>
                  targetArr.includes(item)
                );
                if (hasCommonElement) {
                  return true;
                }
                return false;
              }}
              className={
                (left ? "-ml-0.5 " : "-mr-0.5 ") +
                "w-3 h-3 rounded-full border-2 bg-white dark:bg-gray-800"
              }
              style={{
                borderColor: color,
                top: position,
              }}
            ></Handle>
          </Tooltip>
        )}

        {left === true &&
        type === "str" &&
        !data?.node?.template[name].options ? (
          <div className="mt-2 w-full">
            {data?.node?.template[name].list ? (
              <InputListComponent
                disabled={false}
                value={
                  !data.node.template[name].value ||
                  data.node.template[name].value === ""
                    ? [""]
                    : data.node.template[name].value
                }
                onChange={(t: string[]) => {
                  alert("jhhjhjhj");

                  if (data?.node?.template?.[name])
                    data.node.template[name].value = t;
                }}
              />
            ) : data?.node?.template[name].multiline ? (
              <TextAreaComponent
                disabled={false}
                value={data?.node.template[name].value ?? ""}
                onChange={(t: string) => {
                  alert("vggg");

                  if (data?.node?.template?.[name])
                    data.node.template[name].value = t;
                }}
              />
            ) : (
              <InputComponent
                // disabled={false}
                password={data?.node?.template[name].password ?? false}
                value={data?.node?.template[name].value ?? ""}
                onChange={(t) => {
                  console.log("t", data?.node?.template?.[name]);
                  if (data?.node?.template?.[name])
                    data.node.template[name].value = t;
                  alert("save");
                }}
              />
            )}
          </div>
        ) : left === true && type === "bool" ? (
          <div className="mt-2">
            <ToggleComponent
              disabled={false}
              enabled={enabled}
              setEnabled={(t) => {
                if (data?.node?.template?.[name])
                  data.node.template[name].value = t;
                setEnabled(t);
                alert("save");
              }}
            />
          </div>
        ) : left === true && type === "float" ? (
          <FloatComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t) => {
              if (data?.node?.template?.[name])
                data.node.template[name].value = t;
            }}
          />
        ) : left === true &&
          type === "str" &&
          data?.node?.template[name].options ? (
          <Dropdown
            options={data.node.template[name].options}
            onSelect={(newValue) => {
              if (data?.node?.template?.[name])
                return (data.node.template[name].value = newValue);
            }}
            value={data.node.template[name].value ?? "Choose an option"}
          ></Dropdown>
        ) : left === true && type === "code" ? (
          <CodeAreaComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t: string) => {
              if (data?.node?.template?.[name])
                data.node.template[name].value = t;
            }}
          />
        ) : left === true && type === "file" ? (
          <InputFileComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t: string) => {
              if (data?.node?.template?.[name])
                data.node.template[name].value = t;
            }}
            fileTypes={data?.node?.template[name].fileTypes}
            suffixes={data?.node?.template[name].suffixes}
            onFileChange={(t: string) => {
              if (data?.node?.template?.[name])
                data.node.template[name].content = t;
            }}
          ></InputFileComponent>
        ) : left === true && type === "int" ? (
          <IntComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t) => {
              if (data?.node?.template?.[name])
                data.node.template[name].value = t;
            }}
          />
        ) : left === true && type === "prompt" ? (
          <PromptAreaComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t: string) => {
              if (data?.node?.template?.[name]) {
                data.node.template[name].value = t;
              }
            }}
          />
        ) : (
          <></>
        )}
      </>
    </div>
  );
}

import { Tooltip } from "@mui/material";
import { useRef, useState, useEffect, useContext } from "react";
import { Handle, Position, useUpdateNodeInternals } from "reactflow";
import { NodeDataType, ParameterComponentType } from "../constants";
import { nodeColors } from "../utils";
import CodeAreaComponent from "./codeAreaComponent";
import Dropdown from "./dropdownComponent";
import FloatComponent from "./floatComponent";
import InputComponent from "./inputComponent";
import InputFileComponent from "./inputFileComponent";
import InputListComponent from "./inputListComponent";
import IntComponent from "./intComponent";
import PromptAreaComponent from "./promptComponent";
import SvgTrash from "./SvgComps/Trash";
import TextAreaComponent from "./textAreaComponent";
import ToggleComponent from "./toggleComponent";

export const ChainFuryNode = ({ data }: { data: NodeDataType }) => {
  console.log(data);
  return (
    <div
      className={`w-[350px] overflow-hidden border border-light-neutral-grey-200 rounded-[4px] shadow-sm bg-light-system-bg-primary prose-nbx`}
    >
      <div className="flex flex-col">
        <div className="p-[8px] bg-light-system-bg-secondary medium350 flex justify-between items-center border-b">
          <span className="semiBold250 text-light-neutral-grey-500 ">
            {data?.node?.template?._type ?? ""}
          </span>
          <SvgTrash className="stroke-light-neutral-grey-500  cursor-pointer" />
        </div>

        <div className="w-full h-full p-[8px]">
          <div className="w-full text-gray-500 text-sm py-[4px]">
            {data.node?.description}
          </div>

          <>
            {Object.keys(data.node?.template ?? {})
              .filter((t) => t.charAt(0) !== "_")
              .map((t: string, idx) => (
                <div key={idx}>
                  {idx === 0 ? (
                    <div
                      className={
                        (data.node?.template &&
                        Object.keys(data.node?.template)?.filter(
                          (key) =>
                            !key.startsWith("_") &&
                            data?.node?.template?.[key]?.show
                        ).length === 0
                          ? "hidden"
                          : "") +
                        "medium400 text-light-neutral-grey-600 flex items-center gap-[4px] py-[8px]"
                      }
                    >
                      Inputs{" "}
                      <div className="w-full bg-light-neutral-grey-200 h-px"></div>
                    </div>
                  ) : (
                    <></>
                  )}
                  {data?.node?.template[t].show ? (
                    <ParameterComponent
                      data={data}
                      color={
                        // nodeColors[data?.node?.template?[t].type ?? ''] ??
                        nodeColors.unknown
                      }
                      title={
                        data?.node?.template[t].display_name
                          ? data.node.template[t].display_name
                          : data.node?.template[t].name ?? t
                      }
                      name={t}
                      tooltipTitle={
                        "Type: " +
                        data.node.template[t].type +
                        (data.node.template[t].list ? " list" : "")
                      }
                      required={data.node.template[t].required}
                      id={data.node.template[t].type + "|" + t + "|" + data.id}
                      left={true}
                      type={data.node.template[t].type}
                    />
                  ) : (
                    <></>
                  )}
                </div>
              ))}
          </>
        </div>
        <div className="py-[8px] flex flex-col gap-[8px]">
          <span className="medium400 text-light-neutral-grey-600 flex items-center gap-[4px] p-[8px]">
            Output
          </span>
          <ParameterComponent
            data={data}
            color={nodeColors.unknown}
            title={data?.node?.template?._type ?? ""}
            tooltipTitle={`Type: ${data?.node?.base_classes.join(" | ")}`}
            id={[data.type, data.id, ...(data?.node?.base_classes ?? [])]?.join(
              "|"
            )}
            type={data?.node?.base_classes?.join("|") ?? ""}
            left={false}
          />
        </div>
      </div>
    </div>
  );
};

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
                return true;
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
                  if (data?.node?.template?.[name]?.value)
                    data.node.template[name].value = t;
                  //////alert("save");
                }}
              />
            ) : data?.node?.template[name].multiline ? (
              <TextAreaComponent
                disabled={false}
                value={data?.node.template[name].value ?? ""}
                onChange={(t: string) => {
                  if (data?.node?.template?.[name]?.value)
                    data.node.template[name].value = t;
                  //////alert("save");
                }}
              />
            ) : (
              <InputComponent
                // disabled={false}
                password={data?.node?.template[name].password ?? false}
                value={data?.node?.template[name].value ?? ""}
                onChange={(t) => {
                  if (data?.node?.template?.[name]?.value)
                    data.node.template[name].value = t;
                  //////alert("save");
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
                if (data?.node?.template?.[name]?.value)
                  data.node.template[name].value = t;
                setEnabled(t);
                //////alert("save");
              }}
            />
          </div>
        ) : left === true && type === "float" ? (
          <FloatComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t) => {
              if (data?.node?.template?.[name]?.value)
                data.node.template[name].value = t;
              ////alert("save");
            }}
          />
        ) : left === true &&
          type === "str" &&
          data?.node?.template[name].options ? (
          <Dropdown
            options={data.node.template[name].options}
            onSelect={(newValue) => {
              if (data?.node?.template?.[name]?.value)
                return (data.node.template[name].value = newValue);
            }}
            value={data.node.template[name].value ?? "Choose an option"}
          ></Dropdown>
        ) : left === true && type === "code" ? (
          <CodeAreaComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t: string) => {
              if (data?.node?.template?.[name]?.value)
                data.node.template[name].value = t;
              ////alert("save");
            }}
          />
        ) : left === true && type === "file" ? (
          <InputFileComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t: string) => {
              if (data?.node?.template?.[name]?.value)
                data.node.template[name].value = t;
            }}
            fileTypes={data?.node?.template[name].fileTypes}
            suffixes={data?.node?.template[name].suffixes}
            onFileChange={(t: string) => {
              if (data?.node?.template?.[name]?.value)
                data.node.template[name].content = t;
              ////alert("save");
            }}
          ></InputFileComponent>
        ) : left === true && type === "int" ? (
          <IntComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t) => {
              if (data?.node?.template?.[name]?.value)
                data.node.template[name].value = t;
              ////alert("save");
            }}
          />
        ) : left === true && type === "prompt" ? (
          <PromptAreaComponent
            disabled={false}
            value={data?.node?.template[name].value ?? ""}
            onChange={(t: string) => {
              if (data?.node?.template?.[name]?.value) {
                data.node.template[name].value = t;
                ////alert("save");
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

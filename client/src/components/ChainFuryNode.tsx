import { NodeDataType } from "../constants";
import { nodeColors } from "../utils";
import ParameterComponent from "./ParameterComponent";
import SvgTrash from "./SvgComps/Trash";

export const ChainFuryNode = ({ data }: { data: NodeDataType }) => {
  return (
    <div
      className={`w-[350px] overflow-hidden border border-light-neutral-grey-200 rounded-[4px] shadow-sm bg-light-system-bg-primary prose-nbx`}
    >
      <div className="flex flex-col">
        <div className="p-[8px] bg-light-system-bg-secondary medium350 flex justify-between items-center border-b">
          <span className="semiBold250 text-light-neutral-grey-500 ">
            {data?.node?.template?._type ?? ""}
          </span>
          <div
            className="cursor-pointer"
            onClick={() => {
              console.log("delete", data);
              data?.deleteMe?.();
            }}
          >
            <SvgTrash className="stroke-light-neutral-grey-500" />
          </div>
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
                      color={nodeColors[data?.node?.chain ?? ""]}
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
            color={nodeColors[data?.node?.chain ?? ""]}
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

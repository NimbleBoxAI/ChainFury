import { Dialog } from "@mui/material";
import { useEffect, useState } from "react";
import { useAuthStates } from "../redux/hooks/dispatchHooks";
import { useGetStepsMutation } from "../redux/services/auth";
import SvgClose from "./SvgComps/Close";

export function Table({
  label,
  headings,
  spacing,
  values,
}: {
  label?: string;
  headings: string[];
  spacing?: number[];
  values: (string | number)[][];
}) {
  const [selectedRow, setSelectedRow] = useState(-1);
  const { auth } = useAuthStates();

  const TableDialog = ({ onClose }: { onClose: () => void }) => {
    const [getSteps] = useGetStepsMutation();
    const [responses, setResponses] = useState(
      [] as {
        ques: string;
        ans: string;
      }[]
    );

    useEffect(() => {
      getSteps({
        id: auth?.selectedChatBot?.id,
        prompt_id: values[selectedRow]?.[0] + "",
        token: auth?.accessToken,
      })
        .unwrap()
        .then((res) => {
          setResponses(
            res.data?.length
              ? res.data.map(
                  (val: {
                    intermediate_response: any;
                    intermediate_prompt: any;
                  }) => {
                    return {
                      ques: val.intermediate_response,
                      ans: val.intermediate_prompt,
                    };
                  }
                )
              : []
          );
        })
        .catch((err) => {
          console.log(err);
        });
    }, []);
    return (
      <Dialog open={true} onClose={onClose}>
        <div
          className={`prose-nbx max-h-[90vh] overflow-hidden relative  gap-[16px] p-[16px] flex flex-col justify-center w-[500px]`}
        >
          <SvgClose
            onClick={onClose}
            className="stroke-light-neutral-grey-900 absolute right-[8px] top-[8px] scale-[1.2] cursor-pointer"
          />
          <div className="flex flex-col">
            {headings?.map((value, id) => (
              <div key={id} className="flex py-[8px] flex-col">
                <span className="semiBold250">{value}</span>
                <span className="medium250">
                  {values[selectedRow]?.[id] ?? "-"}
                </span>
              </div>
            ))}
          </div>{" "}
          {responses?.length ? (
            <>
              <span className="semiBold250">Intermediate Steps</span>
              <div className="flex py-[8px] flex-col overflow-scroll h-full">
                <div className="flex flex-col">
                  {responses?.map((val, index) => (
                    <div key={index}>
                      <div className={`chat nbx-chat-end`}>
                        <div className="chat-bubble medium250">{val?.ans}</div>
                      </div>{" "}
                      <div className={`chat nbx-chat-start`}>
                        <div className="chat-bubble medium250">{val?.ques}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            ""
          )}
        </div>
      </Dialog>
    );
  };

  return (
    <>
      {selectedRow >= 0 ? (
        <TableDialog
          onClose={() => {
            setSelectedRow(-1);
          }}
        />
      ) : (
        ""
      )}
      <div className="overflow-x-auto relative rounded-[4px] prose-nbx">
        {label ? <span className="semiBold400">{label}</span> : ""}
        <table draggable className="w-full text-sm text-left ">
          <tbody>
            <tr className="flex bg-light-neutral-grey-100 semiBold250 text-light-neutral-grey-700 rounded-md">
              {headings?.map((val, index) => (
                <th
                  key={index}
                  style={{
                    flex: spacing?.[index] || 1,
                  }}
                  scope="col"
                  className="p-[12px] min-w-[170px]"
                >
                  {val}
                </th>
              ))}
            </tr>
            {values?.map((row, index) => (
              <tr
                onClick={() => {
                  setSelectedRow(index);
                }}
                className={`flex regular250 cursor-pointer hover:bg-light-primary-blue-50 ${
                  index % 2 ? "bg-light-neutral-grey-100" : ""
                }`}
                key={index}
              >
                {headings?.map((val, key) => {
                  return (
                    <td
                      style={{
                        flex: spacing?.[key] || 1,
                      }}
                      scope="row"
                      key={key}
                      className="p-[12px] min-w-[170px] text-ellipsis h-[48px] truncate"
                    >
                      {row[key]}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

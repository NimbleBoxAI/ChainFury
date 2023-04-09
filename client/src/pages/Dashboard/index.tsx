import { Button } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ChatComp from "../../components/ChatComp";
import LineChart from "../../components/LineChart";
import SvgCopy from "../../components/SvgComps/Copy";
import { Table } from "../../components/Table";
import { useAuthStates } from "../../redux/hooks/dispatchHooks";
import { useAppDispatch } from "../../redux/hooks/store";
import { useGetPromptsMutation } from "../../redux/services/auth";
import { setPrompts } from "../../redux/slices/authSlice";

const Dashboard = () => {
  const { auth } = useAuthStates();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [getPrompts] = useGetPromptsMutation();
  const [latencies, setLatencies] = useState(
    [] as {
      name: string;
      time: number;
      created_at: number;
    }[]
  );

  useEffect(() => {
    if (auth?.selectedChatBot?.id) {
      getPrompts({ id: auth?.selectedChatBot?.id, token: auth?.accessToken })
        ?.unwrap()
        .then((res) => {
          dispatch(
            setPrompts({
              prompts: res.data,
              chatbot_id: auth?.selectedChatBot?.id,
            })
          );
        })
        .catch((err) => {
          alert("Unable to fetch prompts");
        });
    }
  }, [auth.selectedChatBot]);

  useEffect(() => {
    if (auth.selectedChatBot && auth?.prompts?.[auth?.selectedChatBot?.id]) {
      const prompts = auth?.prompts?.[auth?.selectedChatBot?.id];
      const latencies = prompts.map((prompt) => {
        return {
          name: prompt.input_prompt,
          time: Math.round(prompt.time_taken),
          created_at: new Date(prompt.created_at).getTime(),
        };
      });
      setLatencies(latencies);
    }
  }, [auth.prompts, auth.selectedChatBot]);

  const embeddedScript = `<script>
  window.onload = function () {
    const iframe = document.createElement("iframe");
    iframe.src = "${window?.location?.protocol}://${window?.location?.host}/chat/${auth?.selectedChatBot?.id}";
    iframe.style.position = "absolute";
    iframe.style.zIndex = "10000";
    iframe.style.bottom = "0";
    iframe.style.right = "0";
    iframe.style.width = "350px";
    iframe.style.height = "450px";
    document.body.appendChild(iframe);
  };
  </script>`;

  return (
    <div className="bg-light-system-bg-primary prose-nbx p-[24px] w-full ">
      {auth?.selectedChatBot?.name ? (
        <>
          <div className="flex justify-between items-center w-full">
            <span className="semiBold600">{auth?.selectedChatBot?.name}</span>
            <Button
              variant="outlined"
              className="h-[24px]"
              color="primary"
              onClick={() => {
                navigate(`/ui/dashboard/${auth?.selectedChatBot?.id}`);
              }}
            >
              Edit
            </Button>
          </div>
          <div className="overflow-scroll h-full w-[calc(100%-270px)]">
            <div className="flex gap-[8px] mt-[32px] flex-col">
              <span>
                Embed the bot on your website by adding the following code to
                your HTML
              </span>
              <div className="relative">
                <SvgCopy
                  className="stroke-light-neutral-grey-700 absolute right-[8px] top-[8px] cursor-pointer"
                  onClick={() => {
                    navigator.clipboard.writeText(embeddedScript);
                  }}
                />
                <pre className="regular300 font-mono rounded-md bg-light-neutral-grey-200 text-light-neutral-grey-600 w-[full] p-[16px] overflow-scroll max-h-[150px]">
                  {embeddedScript}
                </pre>
              </div>
            </div>
            <div className="flex flex-wrap gap-[8px] justify-between mt-[32px]">
              <div className="w-[500px] h-[250px] overflow-hidden">
                <span className="semiBold350">Latency</span>
                <LineChart
                  xAxis={{
                    formatter: " ",
                    data: latencies.map((latency) => latency.created_at),
                    type: "time",
                  }}
                  yAxis={{
                    formatter: "s",
                  }}
                  series={[
                    {
                      name: "Time taken",
                      data: latencies.map((latency) => latency.time),
                    },
                  ]}
                />
              </div>
            </div>

            <Table
              label="Prompts"
              values={auth?.prompts?.[auth?.selectedChatBot?.id]?.map(
                (prompt) => [
                  prompt?.id,
                  prompt?.input_prompt,
                  prompt?.user_rating ?? "",
                  prompt?.response,
                  prompt?.gpt_rating ?? "",
                  Math.round(prompt?.time_taken) + "s",
                  "-",
                ]
              )}
              headings={[
                "Prompt ID",
                "Input Prompt",
                "User Ratings",
                "Final Prompt",
                "GPT Rating",
                "Response Time",
                "# of Tokens",
              ]}
            />
          </div>
        </>
      ) : (
        ""
      )}
      <div className="h-[450px] w-[350px] absolute bottom-0 right-0">
        <ChatComp chatId={auth?.selectedChatBot?.id} />
      </div>
    </div>
  );
};

export default Dashboard;

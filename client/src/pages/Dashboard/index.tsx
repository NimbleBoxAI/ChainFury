import { Button } from "@mui/material";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ChatComp from "../../components/ChatComp";
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

  return (
    <div className="bg-light-system-bg-primary prose-nbx p-[24px] w-full overflow-hidden">
      {auth?.selectedChatBot?.name ? (
        <>
          <div className="flex justify-between items-center w-full">
            <span className="semiBold600">{auth?.selectedChatBot?.name}</span>
            <Button
              variant="outlined"
              className="h-[24px]"
              color="primary"
              onClick={() => {
                navigate(`/dashboard/${auth?.selectedChatBot?.id}`);
              }}
            >
              Edit
            </Button>
          </div>
          <div className="flex gap-[8px] mt-[32px] flex-col">
            <span>
              Embed the bot on your website by adding the following code to your
              HTML
            </span>
            <div className="relative">
              <SvgCopy className="stroke-light-neutral-grey-700 absolute right-[8px] top-[8px] cursor-pointer" />
              <pre className="regular300 font-mono rounded-md bg-light-neutral-grey-200 text-light-neutral-grey-600 w-[full] p-[16px] overflow-scroll max-h-[150px]">
                {`<script>
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
</script>`}
              </pre>
            </div>
          </div>
          <div className="flex flex-wrap gap-[8px] justify-between mt-[32px]">
            <ScoreCard title="Latency" value="00" />
            <ScoreCard title="#Token" value="00" />
            <ScoreCard title="User Score" value="00" />
            <ScoreCard title="Internal Review Score" value="00" />
            <ScoreCard title="GPT Rating" value="5" />
          </div>

          <Table
            label="Prompts"
            values={auth?.prompts?.[auth?.selectedChatBot?.id]?.map(
              (prompt) => [
                prompt?.input_prompt,
                "-",
                prompt?.user_rating ?? "",
                prompt?.response,
                prompt?.gpt_rating ?? "",
                prompt?.time_taken + "",
                "-",
              ]
            )}
            headings={[
              "Input Prompt",
              "Intermediate Steps",
              "User Ratings",
              "Final Propmt",
              "GPT Rating",
              "Response Time",
              "# of Tokens",
            ]}
          />
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

const ScoreCard = ({ title, value }: { title: string; value: string }) => (
  <div className="shadow-md p-[8px] gap-[8px] flex flex-col rounded-md w-[200px] border border-light-neutral-grey-200  prose-nbx">
    <span className="medium300">{title}</span>
    <span className="semiBold800">{value}</span>
  </div>
);

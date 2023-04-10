import { Button } from '@mui/material';
import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import ChatComp from '../../components/ChatComp';
import LineChart from '../../components/LineChart';
import PieChart from '../../components/PieChart';
import SvgCopy from '../../components/SvgComps/Copy';
import { Table } from '../../components/Table';
import { useAuthStates } from '../../redux/hooks/dispatchHooks';
import { useAppDispatch } from '../../redux/hooks/store';
import { useGetMetricsMutation, useGetPromptsMutation } from '../../redux/services/auth';
import { setPrompts, setSelectedChatBot } from '../../redux/slices/authSlice';

const metrics = ['latency', 'user_score', 'internal_review_score', 'gpt_review_score'];
interface FeedbackInterface {
  bad_count: number;
  good_count: number;
  neutral_count: number;
}

const Dashboard = () => {
  const { auth } = useAuthStates();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [getPrompts] = useGetPromptsMutation();
  const [getMetrics] = useGetMetricsMutation();
  const [metricsInfo, setMetricsInfo] = useState({} as Record<string, FeedbackInterface>);
  const [latencies, setLatencies] = useState(
    [] as {
      time: number;
      created_at: number;
    }[]
  );
  const [searchParams] = useSearchParams();

  useEffect(() => {
    if (searchParams?.get('id') && auth?.chatBots?.[searchParams?.get('id') ?? '']) {
      dispatch(setSelectedChatBot({ chatBot: auth?.chatBots?.[searchParams?.get('id') ?? ''] }));
    }
  }, [auth.chatBots, searchParams]);

  useEffect(() => {
    if (auth?.selectedChatBot?.id) {
      getPrompts({ id: auth?.selectedChatBot?.id, token: auth?.accessToken })
        ?.unwrap()
        .then((res) => {
          dispatch(
            setPrompts({
              prompts: res.data,
              chatbot_id: auth?.selectedChatBot?.id
            })
          );
        })
        .catch(() => {
          alert('Unable to fetch prompts');
        });
      getMetricsDetails();
    }
  }, [auth?.selectedChatBot?.id]);

  const getMetricsDetails = async () => {
    await metrics?.forEach(async (metric) => {
      getMetrics({
        id: auth?.selectedChatBot?.id,
        token: auth?.accessToken,
        metric_type: metric
      })
        ?.unwrap()
        ?.then((res) => {
          if (metric === 'latency') {
            setLatencies(res.data);
          } else
            setMetricsInfo((prev) => {
              return {
                ...prev,
                [metric]: res.data?.[0]
              };
            });
        });
    });
  };

  const embeddedScript = `<script type="text/javascript" >
  window.onload = function () {
    const iframe = document.createElement("iframe");
    iframe.src = "${window?.location?.protocol}//${window?.location?.host}/ui/chat/${auth?.selectedChatBot?.id}";
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
                navigate(`/ui/dashboard/${auth?.selectedChatBot?.id}`);
              }}
            >
              Edit
            </Button>
          </div>
          <div className="overflow-scroll h-full w-full">
            <div className="flex gap-[8px] mt-[32px] flex-col">
              <span>Embed the bot on your website by adding the following code to your HTML</span>
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
            {latencies.length > 0 ? (
              <div className="w-full h-[250px] overflow-hidden mt-[32px]">
                <span className="semiBold350">Latency</span>
                <LineChart
                  xAxis={{
                    formatter: ' ',
                    data: latencies.map((latency) => new Date(latency.created_at).getTime()),
                    type: 'time'
                  }}
                  yAxis={{
                    formatter: 's'
                  }}
                  series={[
                    {
                      name: 'Time taken',
                      data: latencies.map((latency) => Math.round(latency.time * 100) / 100)
                    }
                  ]}
                />
              </div>
            ) : (
              ''
            )}
            <div className="flex flex-wrap gap-x-[8px] gap-y-[16px] justify-between mt-[32px]">
              {metricsInfo?.['user_score']?.good_count ||
              metricsInfo?.['user_score']?.neutral_count ||
              metricsInfo?.['user_score']?.bad_count ? (
                <div className="w-[370px] h-[320px] pb-[20px] overflow-hidden text-center">
                  <span className="semiBold350">USER SCORE</span>
                  <PieChart
                    values={[
                      {
                        name: 'Good',
                        value: metricsInfo?.['user_score']?.good_count
                      },
                      {
                        name: 'Neutral',
                        value: metricsInfo?.['user_score']?.neutral_count
                      },
                      {
                        name: 'Bad',
                        value: metricsInfo?.['user_score']?.bad_count
                      }
                    ]}
                  />
                </div>
              ) : (
                ''
              )}
              {metricsInfo?.['internal_review_score']?.bad_count ||
              metricsInfo?.['internal_review_score']?.good_count ||
              metricsInfo?.['internal_review_score']?.neutral_count ? (
                <div className="w-[370px] h-[320px] pb-[20px] overflow-hidden text-center">
                  <span className="semiBold350">INTERNAL REVIEW SCORE</span>
                  <PieChart
                    values={[
                      {
                        name: 'Good',
                        value: metricsInfo?.['internal_review_score']?.good_count
                      },
                      {
                        name: 'Neutral',
                        value: metricsInfo?.['internal_review_score']?.neutral_count
                      },
                      {
                        name: 'Bad',
                        value: metricsInfo?.['internal_review_score']?.bad_count
                      }
                    ]}
                  />
                </div>
              ) : (
                ''
              )}

              {metricsInfo?.['gpt_review_score']?.bad_count ||
              metricsInfo?.['gpt_review_score']?.good_count ||
              metricsInfo?.['gpt_review_score']?.neutral_count ? (
                <div className="w-[370px] h-[320px] pb-[20px] overflow-hidden text-center">
                  <span className="semiBold350">GPT REVIEW SCORE</span>
                  <PieChart
                    values={[
                      {
                        name: 'Good',
                        value: metricsInfo?.['gpt_review_score']?.good_count
                      },
                      {
                        name: 'Neutral',
                        value: metricsInfo?.['gpt_review_score']?.neutral_count
                      },
                      {
                        name: 'Bad',
                        value: metricsInfo?.['gpt_review_score']?.bad_count
                      }
                    ]}
                  />
                </div>
              ) : (
                ''
              )}
            </div>

            {auth?.prompts?.[auth?.selectedChatBot?.id]?.length ? (
              <Table
                label="Prompts"
                values={auth?.prompts?.[auth?.selectedChatBot?.id]?.map((prompt) => [
                  prompt?.id,
                  prompt?.input_prompt,
                  prompt?.response,
                  prompt?.user_rating ?? '',
                  prompt?.gpt_rating ?? '',
                  prompt?.num_tokens ?? '',
                  Math.round(prompt?.time_taken) + 's'
                ])}
                headings={[
                  'Prompt ID',
                  'Input Prompt',
                  'Final Prompt',
                  'User Ratings',
                  'GPT Rating',
                  '# of Tokens',
                  'Response Time'
                ]}
              />
            ) : (
              ''
            )}
          </div>
        </>
      ) : (
        ''
      )}
      <div className="h-[450px] w-[350px] absolute bottom-0 right-0">
        <ChatComp chatId={auth?.selectedChatBot?.id} />
      </div>
    </div>
  );
};

export default Dashboard;

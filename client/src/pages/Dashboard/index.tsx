import { Button } from '@mui/material';
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import ChatComp from '../../components/ChatComp';
import LineChart from '../../components/LineChart';
import PieChart from '../../components/PieChart';
import SvgCopy from '../../components/SvgComps/Copy';
import { Table } from '../../components/Table';
import { DummyMetricsData, DummyMetricsInfo } from '../../constants';
import { useAuthStates } from '../../redux/hooks/dispatchHooks';
import { useAppDispatch } from '../../redux/hooks/store';
import {
  useGetMetricsMutation,
  useGetPromptsMutation
} from '../../redux/services/auth';
import {
  MetricsInterface,
  setMetrics,
  setPrompts,
  setSelectedChatBot
} from '../../redux/slices/authSlice';

interface FeedbackInterface {
  bad_count: number;
  good_count: number;
  neutral_count: number;
}

const Dashboard = () => {
  const [showDummyData, setShowDummyData] = useState(false);
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
  const [chainMetrics, setMetrics] = useState(
    {} as MetricsInterface
  )

  useEffect(() => {
    if (searchParams?.get('id') && auth?.chatBots?.[searchParams?.get('id') ?? '']) {
      dispatch(setSelectedChatBot({ chatBot: auth?.chatBots?.[searchParams?.get('id') ?? ''] }));
    }
    if (auth?.chatBots && Object.values(auth?.chatBots).length > 0) {
      setShowDummyData(false);
    } else if (!searchParams?.get('id')) {
      setShowDummyData(true);
    }
  }, [auth.chatBots, searchParams]);

  useEffect(() => {
    if (auth?.selectedChatBot?.id) {
      getPrompts({ id: auth?.selectedChatBot?.id, token: auth?.accessToken })
        ?.unwrap()
        .then((res) => {
          dispatch(
            setPrompts({
              prompts: res?.prompts,
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
    getMetrics({
      chain_id: auth?.selectedChatBot?.id,
      token: auth?.accessToken,
    })
      ?.unwrap()
      ?.then((res) => {
        setMetrics(res?.metrics);
        setLatencies(res?.latencies);
        console.log(res);
      });
  };

  const embeddedScript = `<script src="${window?.location?.origin}/script/embedBot.js?chatBotId=${auth?.selectedChatBot?.id}" type="text/javascript"></script>`;

  return (
    <div className="relative w-full h-full">
      <div className="bg-light-system-bg-primary prose-nbx p-[24px] w-full h-full overflow-hidden">
        {auth?.selectedChatBot?.name || showDummyData ? (
          <>
            <div className="flex justify-between items-center w-full">
              <span className="semiBold600">{auth?.selectedChatBot?.name ?? 'Nimblebox Bot'}</span>
              {/* <Button
                variant="outlined"
                className="h-[24px]"
                color="primary"
                onClick={() => {
                  navigate(`/ui/dashboard/${auth?.selectedChatBot?.id}`);
                }}
              >
                Edit
              </Button> */}
            </div>
            <div className="overflow-scroll h-full w-full">
              {chainMetrics ? (
                <BotMetrics
                  metricsInfo={chainMetrics}
                />
              ) : (
                ''
              )}
              <div className="flex gap-[8px] mt-[32px] flex-col">
                <span className="medium300">
                  Clicking on bottom chat icon to run <span className="semiBold300">{auth?.selectedChatBot?.name} </span>
                  Or embed the bot on your website by adding the following code to your HTML
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
              {latencies.length > 0 ? (
                <div className="w-full h-[250px] overflow-hidden mt-[32px]">
                  <span className="semiBold350">Latency over last 24 hours</span>
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
                <div className="w-full h-[64px] overflow-hidden mt-[32px]">
                  <span className="semiBold350">No usage in last 24 hours 🙁, use to track metrics</span>
                </div>
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
                    new Date(prompt?.created_at).toLocaleString() + " UTC",
                    Math.round(prompt?.time_taken) + 's',
                    prompt?.input_prompt,
                    prompt?.response,
                  ])}
                  headings={[
                    'ID',
                    'Timestamp',
                    'Response Time',
                    'Input Prompt',
                    'Final Prompt',
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
        {auth?.selectedChatBot?.id ? (
          <div className="h-[450px] w-[350px] absolute bottom-0 right-0">
            <ChatComp chatId={auth?.selectedChatBot?.id} />
          </div>
        ) : (
          ''
        )}
      </div>
      {showDummyData ? (
        <div className="absolute prose-nbx flex justify-center items-center w-[calc(100%+60px)] h-screen bg-light-neutral-grey-200 bg-opacity-40 z-100 top-0 ">
          <div className="bg-white rounded-md shadow-md w-full max-w-[400px] flex flex-col justify-center items-center text-center gap-[4px] p-[32px]">
            <span className="semiBold400">No Chatsbots found.</span>
            <span className="medium250">Please create a chatbot to view the dashboard.</span>
          </div>
        </div>
      ) : (
        ''
      )}
    </div>
  );
};

export default Dashboard;

const BotMetrics = ({ metricsInfo }: { metricsInfo: MetricsInterface }) => {
  return (
    <>
      <div className="flex flex-wrap w-full gap-[16px] mt-[32px]">
        <div className="w-[190px] rounded-md cursor-pointer flex flex-col h-[130px] p-[16px] border-[1px] border-solid border-light-neutral-grey-200 dark:border-dark-neutral-grey-200">
          <div className="flex gap-[8px] items-center">
            <span className="medium250 text-light-neutral-grey-700 dark:text-dark-neutral-grey-700">
              Total Usage
            </span>
          </div>
          <span className="medium800 mt-[8px] text-light-neutral-grey-900 dark:text-dark-neutral-grey-900">
            {metricsInfo?.['total_conversations']}
          </span>
        </div>
      </div>
    </>
  );
};

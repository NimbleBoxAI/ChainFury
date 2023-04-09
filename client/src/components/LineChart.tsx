import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import moment from "moment";

export interface axisInterface {
  data?: string[] | number[];
  formatter: string | boolean; // if false then no label will be shown, if empty string then it will be the value,
  type?: string;
}
export interface seriesInterface {
  name: string;
  data: number[];
  colour?: string; // if not set, it will be the default colour
}
export interface markAreaInterface {
  colour: string;
  data: {
    from: number | string;
    to: number | string;
    name: string;
  }[];
}

const LineChart = ({
  xAxis,
  yAxis,
  series,
  markArea,
  smooth = 0.1,
}: {
  xAxis: axisInterface;
  yAxis: axisInterface;
  series: seriesInterface[];
  markArea?: markAreaInterface;
  smooth?: number;
}) => {
  const [options, setOptions] = useState({});
  const [seriesColorMap, setSeriesColorMap] = useState(
    {} as Record<string, string>
  );

  useEffect(() => {
    const tempSeriesColorMap = {} as any;
    series.map((val) => {
      tempSeriesColorMap[val?.name] = "#006EF5";
    });
    setSeriesColorMap(tempSeriesColorMap);
  }, [series]);

  useEffect(() => {
    if (Object?.values(seriesColorMap).length) formatOptions();
  }, [seriesColorMap]);

  const formatOptions = () => {
    const optionsTemplate = {
      color: "#006EF5",
      tooltip: {
        trigger: "axis",
        position: "top",
        formatter: (params: any[]) => {
          return `
          <div style="min-width:150px" class="flex regular200 flex-col">${
            xAxis?.type !== "time"
              ? params?.[0].name
              : moment(Number(params?.[0].name)).format("DD MMM YYYY HH:mm:ss")
          }<br/>${params?.map((val) => {
            const icon = `<span style="background-color: ${
              seriesColorMap[val.seriesName]
            };border-radius:50%;display:block;height:8px;width:8px;"></span>`;
            return `<div class="flex gap-[4px] items-center w-full" >${icon} <span class="w-full flex items-center justify-between">
            ${val.seriesName} <strong>${val.value + "s"}</strong>
            </div></span>`;
          })}
          <div/>`.replaceAll(",", "");
        },
      },
      grid: {
        top: "8%",
        left: "3%",
        right: "3%",
        bottom: "32%",
        containLabel: true,
      },
      xAxis: {
        type: "category",
        boundaryGap: false,
        axisLabel: {
          formatter: "" as any,
        },
        data: undefined as string[] | number[] | undefined,
      },
      yAxis: {
        type: "value",
        axisLabel: {
          formatter: "" as string | undefined,
        },
        data: undefined as string[] | number[] | undefined,
      },
      series: [] as seriesInterface[],
    };
    if (xAxis?.data) {
      optionsTemplate.xAxis.data = xAxis.data;
    }

    if (yAxis?.data) {
      optionsTemplate.yAxis.data = yAxis.data;
    }

    if (xAxis?.formatter && xAxis?.type !== "time") {
      optionsTemplate.xAxis.axisLabel.formatter = `{value} ${xAxis.formatter}`;
    } else if (xAxis?.type === "time") {
      optionsTemplate.xAxis.axisLabel.formatter = function (value: any) {
        return moment(Number(value)).format("HH:mm:ss");
      };
    }

    if (yAxis?.formatter) {
      optionsTemplate.yAxis.axisLabel.formatter = `{value} ${yAxis.formatter}`;
    }

    const seriesData = series.map(({ name, data }) => {
      return {
        name,
        data,
        type: "line",
        showSymbol: false,
        smooth: smooth,
        encode: {
          tooltip: "y",
        },
        lineStyle: { color: "#006EF5" },
        markArea: undefined as any,
      };
    });

    if (markArea) {
      const tempData = markArea.data?.map((val) => [
        {
          name: val.name,
          xAxis: val.from,
        },
        {
          name: val.name,
          xAxis: val.to,
        },
      ]);
      seriesData[0]["markArea"] = {
        itemStyle: {
          color: "rgba(255, 173, 177, 0.4)",
        },
        data: tempData,
      };
    }

    optionsTemplate.series = seriesData;

    setOptions(optionsTemplate);
  };

  return (
    <>
      {Object.keys(seriesColorMap).length ? (
        <ReactECharts
          notMerge={true}
          className="p-0 m-0 w-full"
          option={options}
        />
      ) : (
        ""
      )}
    </>
  );
};

export default LineChart;

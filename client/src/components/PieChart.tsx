import ReactECharts from 'echarts-for-react';

const PieChart = ({ values }: { values: { name: string; value: number }[] }) => {
  const options = {
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        name: '',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        data: values
      }
    ]
  };
  return (
    <>
      {values?.length ? (
        <ReactECharts notMerge={true} className="p-0 m-0 w-full" option={options} />
      ) : (
        ''
      )}
    </>
  );
};

export default PieChart;

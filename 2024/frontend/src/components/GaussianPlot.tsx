import { Chart, Scale } from 'chart.js/auto';
import { Line } from 'react-chartjs-2';
import * as math from 'mathjs';
import {CategoryScale, Tick} from 'chart.js';

function GaussianPlot({ mean, sigma } : { mean: number, sigma: number}) {
    Chart.register(CategoryScale);

    const x = math.range(math.round(mean-3*sigma), math.round(mean+3*sigma), 0.1).toArray() as number[];
  const y = x.map((val:number) => (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((val - mean) / sigma, 2) ));

  const data = {
    labels: x,
    datasets: [
      {
        label: 'Red Advantage',
        data: y,
        fill: true,
        backgroundColor: 'rgba(255, 0, 0, 0.2)',
        borderColor: 'rgba(255, 0, 0, 0.2)',
      },
    ],
  };

  const options = {
    scales: {
      x: {
        ticks: {
            callback: function(this: Scale, tickValue: number | string, index: number, ticks: Tick[]) : string {
              console.log(tickValue, index, ticks[index], this.getLabelForValue(tickValue as number));
              //return this.getLabelForValue(value).toFixed(0); //  return (value as number).toFixed(0);
              return Number.parseInt(this.getLabelForValue(tickValue as number)).toFixed(0);
            }
          }
      }
    }
  };

  return <Line data={data} options={options}/>;
}

export default GaussianPlot;
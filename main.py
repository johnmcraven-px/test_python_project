from fastapi import FastAPI
from typing import Dict
import altair as alt
import pandas as pd
from vega_datasets import data
import json
from dashboardTypes import DashboardResponse

source = data.cars()

alt.Chart(source).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).interactive()

app = FastAPI()


def getLayout():
    return """{
  "content": [
    {
      "type": "row",
      "content": [
        {
          "type": "component",
          "componentName": "VegaLiteChart",
          "componentState": {
            "specId": "A"
          }
        },
        {
          "type": "component",
          "componentName": "VegaLiteChart",
          "componentState": {
            "specId": "B"
          }
        }
      ]
    }
  ]
}"""

@app.get("/initialize")
def read_root():
    vegaSpecs: Dict[str, str] = {}

    def addChartSpec(key: str, chart: alt.Chart): 
        vega_lite_spec = chart.to_dict()
        vega_lite_spec_str = json.dumps(vega_lite_spec)
        vegaSpecs[key] = vega_lite_spec_str

    sourceA = pd.DataFrame({
        'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
        'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
    })

    addChartSpec("A", alt.Chart(sourceA).mark_bar().encode(
        x='a',
        y='b'
    ))
    sourceB = data.cars()

    addChartSpec("B", alt.Chart(sourceB).mark_circle(size=60).encode(
        x='Horsepower',
        y='Miles_per_Gallon',
        color='Origin',
        tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
    ).interactive())

    return DashboardResponse(goldenLayoutJsonStr=getLayout(), vegaSpecs=vegaSpecs)



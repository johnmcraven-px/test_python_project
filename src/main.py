from fastapi import FastAPI
from typing import Dict
import altair as alt
import pandas as pd
from vega_datasets import data
import json
from dashboardTypes import DashboardResponse, RowLayoutType, ListLayoutType, ComponentLayoutType, LayoutType, UpdatesFromSignalsRequest, UpdatesFromSignalsResponse, ParamControl

def getLayout() -> LayoutType:
    row1 = RowLayoutType(
        type="row",
        className="items-stretch",
        style=None,
        content=[
            ComponentLayoutType(
                type="component",
                className="flex-1",
                style=None,
                componentName="VegaLiteChart",
                componentState={"specId": "combined_plot", "autoScale": True}
            ),
        ]
    )
    return ListLayoutType(
        type="list",
        className=None,
        style=None,
        content=[
            row1,

        ]
    )
    


app = FastAPI()

lastVegaSpecs: Dict[str, str] | None = None

def generateCharts(initial_selection) -> DashboardResponse:
    vegaSpecs: Dict[str, str] = {}


    def addChartSpec(key: str, chart: alt.Chart): 
        vega_lite_spec = chart.to_dict()
        vega_lite_spec_str = json.dumps(vega_lite_spec)
        vegaSpecs[key] = vega_lite_spec_str

    scatter_data = pd.read_csv("../data/optimize_output/scatter.csv")
    pareto_frontier = pd.read_csv("../data/optimize_output/curve.csv")
    
    scatter_plot = alt.Chart(scatter_data).mark_circle(size=60).encode(
        x='metricX:Q',
        y='metricY:Q',
        color='num_blades:O',  # Color by number of blades
        tooltip=['metricX', 'metricY', 'num_blades', 'blade_length']
    )
    
    # Line plot for the Pareto frontier
    pareto_plot = alt.Chart(pareto_frontier).mark_line(color='red').encode(
        x='metricX:Q',
        y='metricY:Q'
    )
    combined_plot = alt.layer(scatter_plot, pareto_plot).properties(
        title='Scatter Plot with Pareto Frontier'
    )
    addChartSpec("combined_plot", combined_plot)
    return DashboardResponse(layout=getLayout(), vegaSpecs=vegaSpecs)


@app.get("/initialize")
def initialize():
    return generateCharts(None)

# @app.post("/updates_from_signals")
# def update_chart(request: UpdatesFromSignalsRequest) -> UpdatesFromSignalsResponse:
#     return UpdatesFromSignalsResponse(vegaSpecs={})


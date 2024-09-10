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
                componentState={"specId": "loss_vs_epoch", "autoScale": True}
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

    df = pd.read_csv("../data/model_output/training_data.csv")
    loss_vs_epoch = alt.Chart(df).mark_line(point=True).encode(
        x='Epoch:Q',
        y='Loss:Q',
        tooltip=['Epoch', 'Loss']
    ).properties(
        title='Loss vs Epoch'
    )
    addChartSpec("loss_vs_epoch", loss_vs_epoch)
    return DashboardResponse(layout=getLayout(), vegaSpecs=vegaSpecs)


@app.get("/initialize")
def initialize():
    return generateCharts(None)

# @app.post("/updates_from_signals")
# def update_chart(request: UpdatesFromSignalsRequest) -> UpdatesFromSignalsResponse:
#     return UpdatesFromSignalsResponse(vegaSpecs={})


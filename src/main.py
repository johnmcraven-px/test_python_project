from fastapi import FastAPI
from typing import Dict
import altair as alt
import pandas as pd
from vega_datasets import data
import json
from dashboardTypes import DashboardResponse, RowLayoutType, ListLayoutType, ComponentLayoutType, LayoutType, UpdatesFromSignalsRequest, UpdatesFromSignalsResponse

def getLayout() -> LayoutType:
    row = RowLayoutType(
        type="row",
        className="items-stretch",
        style={"minHeight": 400},
        content=[
            ComponentLayoutType(
                type="component",
                className=None,
                style={"minHeight": 400},
                componentName="TransformRunView",
                componentState={}
            ),
        ]
    )
    return ListLayoutType(
        type="list",
        className=None,
        style=None,
        content=[
            row

        ]
    )
    


app = FastAPI()

lastVegaSpecs: Dict[str, str] | None = None

def generateCharts(initial_selection) -> DashboardResponse:
    vegaSpecs: Dict[str, str] = {}
    return DashboardResponse(layout=getLayout(), vegaSpecs=vegaSpecs)


@app.get("/initialize")
def initialize():
    return generateCharts(None)

@app.post("/updates_from_signals")
def update_chart(request: UpdatesFromSignalsRequest) -> UpdatesFromSignalsResponse:
    return UpdatesFromSignalsResponse(vegaSpecs={})


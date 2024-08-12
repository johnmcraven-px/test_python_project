from fastapi import FastAPI
from typing import Dict
import altair as alt
import pandas as pd
from vega_datasets import data
import json
from dashboardTypes import DashboardResponse, RowLayoutType, ListLayoutType, ComponentLayoutType, LayoutType, UpdatesFromSignalsRequest, UpdatesFromSignalsResponse, ParamControl

def getLayout() -> LayoutType:
    blade_length = ParamControl(type="range", labelTitle="blade_length", displayName="Blade Length", numberType="float", defaultStart=5, defaultEnd=5, defaultStep=1)
    num_blades = ParamControl(type="range", labelTitle="num_blades", displayName="Num Blades", numberType="integer", defaultStart=4, defaultEnd=4, defaultStep=1)
    row1 = RowLayoutType(
        type="row",
        className="items-stretch",
        style=None,
        content=[
            ComponentLayoutType(
                type="component",
                className="flex-1",
                style=None,
                componentName="ExperimentSelectorView",
                componentState={"paramControls": [blade_length, num_blades]}
            ),
        ]
    )
    row2 = RowLayoutType(
        type="row",
        className="items-stretch",
        style={"minHeight": 400},
        content=[
            ComponentLayoutType(
                type="component",
                className="flex-1",
                style={"minHeight": 400},
                componentName="TransformRunView",
                componentState={}
            ),
            ComponentLayoutType(
                type="component",
                className="flex-1",
                style={"minHeight": 400},
                componentName="BatchRunTableView",
                componentState={}
            ),
        ]
    )
    return ListLayoutType(
        type="list",
        className=None,
        style=None,
        content=[
            row1,
            row2

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


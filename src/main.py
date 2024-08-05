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
                className="flex-1",
                style=None,
                componentName="VegaLiteChart",
                componentState={"specId": "filtered_chart", "autoScale": True}
            ),
            ComponentLayoutType(
                type="component",
                className="flex-1",
                style=None,
                componentName="StlFileView",
                componentState={"filePath": "/stl/demo.stl"}
            )
        ]
    )
    return ListLayoutType(
        type="list",
        className=None,
        style=None,
        content=[
            ComponentLayoutType(
                type="component",
                className=None,
                style={"minHeight": 400},
                componentName="VegaLiteChart",
                componentState={"specId": "primary_chart", "autoScale": True, "eventTypes": ["clicked_point"]}
            ),
            row

        ]
    )
    


app = FastAPI()

lastVegaSpecs: Dict[str, str] | None = None

def generate_initial_chart(df: pd.DataFrame, initial_selection):
    if initial_selection is None:
        value = None
    else:
        value = [initial_selection]
    selection = alt.selection_single(fields=['Batch', 'Run'], nearest=True, on='click', empty='none', value=value)
    opacity = alt.condition(selection, alt.value(1), alt.value(0.3)) if initial_selection is not None else alt.value(1)
    size = alt.condition(selection, alt.value(200), alt.value(100)) if initial_selection is not None else alt.value(100)
    scatter_plot = alt.Chart(df).mark_circle(size=100).encode(
        x='Performance:Q',
        y='ConstraintSatisfaction:Q',
        color='Batch:N',
        opacity=opacity,
        size=size,
        tooltip=['Batch', 'Run', 'Performance', 'ConstraintSatisfaction', 'Time', 'ParetoScore']
    ).add_selection(
        selection
    ).properties(
        title='Interactive Scatter Plot: Click on a Point'
    )
    return scatter_plot

def generate_filtered_chart(df: pd.DataFrame, selection):
    filtered_df = df
    selected_batch = None
    selected_run = None
    if selection is not None:
        selected_batch = selection['Batch']
        selected_run = selection['Run']
        filtered_df = df[(df['Batch'] == selected_batch) & (df['Run'] == selected_run)]
    
    print("xyzSel", selection, selected_batch, selected_run)
    if selected_batch is None or selected_run is None:
        title = f'Metrics for All Batches and Runs'
    else:
        title = f'Metrics for Batch {selected_batch}, Run {selected_run}'
    filtered_chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X('variable:N', title='Metrics'),
        y=alt.Y('value:Q', title='Value'),
        color=alt.Color('variable:N', legend=None)
    ).transform_fold(
        ['Performance', 'Time', 'ConstraintSatisfaction'],
        as_=['variable', 'value']
    ).properties(
        title=title
    )
    return filtered_chart

def generateCharts(initial_selection) -> DashboardResponse:
    vegaSpecs: Dict[str, str] = {}

    def addChartSpec(key: str, chart: alt.Chart): 
        vega_lite_spec = chart.to_dict()
        vega_lite_spec_str = json.dumps(vega_lite_spec)
        vegaSpecs[key] = vega_lite_spec_str

    # Read csv from ../data/optimization_results.csv into a pandas dataframe
    df = pd.read_csv("../data/optimization_results.csv")
    # df = pd.read_csv("../data/viz_gen/optimization_results_2.csv")


    # Convert Batch to string for categorical encoding
    df['Batch'] = df['Batch'].astype(str)

    primary_chart = generate_initial_chart(df, initial_selection)
    filtered_chart = generate_filtered_chart(df, initial_selection)
    
    addChartSpec("primary_chart", primary_chart)
    addChartSpec("filtered_chart", filtered_chart)

    global lastVegaSpecs
    lastVegaSpecs = vegaSpecs
    return DashboardResponse(layout=getLayout(), vegaSpecs=vegaSpecs)


@app.get("/initialize")
def initialize():
    return generateCharts(None)

@app.post("/updates_from_signals")
def update_chart(request: UpdatesFromSignalsRequest) -> UpdatesFromSignalsResponse:
    print("xyzUC", request)
    primary_chart_signals = request.signals["primary_chart"]
    value = primary_chart_signals["clicked_point"]["datum"] if primary_chart_signals and primary_chart_signals["clicked_point"] and primary_chart_signals["clicked_point"]["datum"] else None
    if value is not None:
        initial_selection = {"Batch": value["Batch"], "Run": value["Run"]}
    else:
        initial_selection = None
    previousVegaSpecs = lastVegaSpecs
    newVegaSpecs = generateCharts(initial_selection).vegaSpecs
    updatedVegaSpecs: Dict[str, str] = {}
    if previousVegaSpecs is None:
        print("xyzPr1")
        updatedVegaSpecs = newVegaSpecs
    else:    
        for key, value in newVegaSpecs.items():
            print("xyzPr2", key)
            if value != previousVegaSpecs[key]:
                print("xyzPr3", key)
                updatedVegaSpecs[key] = value
    return UpdatesFromSignalsResponse(vegaSpecs=updatedVegaSpecs)


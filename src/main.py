from fastapi import FastAPI
from typing import Dict
import altair as alt
import pandas as pd
from vega_datasets import data
import json
from dashboardTypes import DashboardResponse, RowLayoutType, ListLayoutType, ComponentLayoutType, LayoutType, UpdateChartRequest, UpdateChartResponse

def getLayout() -> LayoutType:
    return ListLayoutType(
        type="list",
        className=None,
        style=None,
        content=[
            ComponentLayoutType(
                type="component",
                className="flex-1",
                style=None,
                componentName="VegaLiteChart",
                componentState={"specId": "primary_chart", "autoScale": True}
            ),
            ComponentLayoutType(
                type="component",
                className="flex-1",
                style=None,
                componentName="VegaLiteChart",
                componentState={"specId": "filtered_chart", "autoScale": True}
            )

        ]
    )
    


app = FastAPI()


default_selection = alt.selection_single(fields=['Batch', 'Run'], nearest=True, on='click', empty='none')


def generate_initial_chart(df: pd.DataFrame):
    scatter_plot = alt.Chart(df).mark_circle(size=100).encode(
        x='Performance:Q',
        y='ConstraintSatisfaction:Q',
        color='Batch:N',
        tooltip=['Batch', 'Run', 'Performance', 'ConstraintSatisfaction', 'Time', 'ParetoScore']
    ).properties(
        title='Interactive Scatter Plot: Click on a Point'
    )
    return scatter_plot

def generate_filtered_chart(df: pd.DataFrame, selection):
    selected_batch = selection['fields']['Batch']
    selected_run = selection['fields']['Run']

    filtered_df = df[(df['Batch'] == selected_batch) & (df['Run'] == selected_run)]

    filtered_chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X('variable:N', title='Metrics'),
        y=alt.Y('value:Q', title='Value'),
        color=alt.Color('variable:N', legend=None)
    ).transform_fold(
        ['Performance', 'Time', 'ConstraintSatisfaction'],
        as_=['variable', 'value']
    ).properties(
        title=f'Metrics for Batch {selected_batch}, Run {selected_run}'
    )
    return filtered_chart

def generateCharts(selection) -> DashboardResponse:
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

    primary_chart = generate_initial_chart(df)
    filtered_chart = generate_filtered_chart(df, selection)
    
    addChartSpec("primary_chart", primary_chart)
    addChartSpec("filtered_chart", filtered_chart)

    return DashboardResponse(layout=getLayout(), vegaSpecs=vegaSpecs)


@app.get("/initialize")
def initialize():
    return generateCharts(default_selection)

@app.post("/updated_chart/{spec_id}")
def update_chart(request: UpdateChartRequest) -> UpdateChartResponse:
    selection = request.selection
    return UpdateChartResponse(vegaSpec=generateCharts(selection).vegaSpecs[request.specId])


from fastapi import FastAPI
from typing import Dict
import altair as alt
import pandas as pd
from vega_datasets import data
import json
from dashboardTypes import DashboardResponse, RowLayoutType, ColLayoutType, ComponentLayoutType, LayoutType

source = data.cars()

alt.Chart(source).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).interactive()

app = FastAPI()


def getLayout() -> LayoutType:
    row1 = RowLayoutType(
        type="row",
        className=None,
        content=[
            ComponentLayoutType(
                type="component",
                className=None,
                componentName="VegaLiteChart",
                componentState={"specId": "performance_chart"}
            ),
            ComponentLayoutType(
                type="component",
                className=None,
                componentName="HelloView",
                componentState={"specId": "failure_chart"}
            )
        ]
    )
    row2 = RowLayoutType(
        type="row",
        className=None,
        content=[
            ComponentLayoutType(
                className=None,
                type="component",
                componentName="VegaLiteChart",
                componentState={"specId": "pareto_chart"}
            ),
            ComponentLayoutType(
                type="component",
                className=None,
                componentName="VegaLiteChart",
                componentState={"specId": "comparison_chart_with_line"}
            ),
            ComponentLayoutType(
                type="component",
                className=None,
                componentName="HelloView",
                componentState={"specId": "heatmap"}
            )
        ]
    )

    row3 = RowLayoutType(
        type="row",
        className=None,
        content=[
            ComponentLayoutType(
                className=None,
                type="component",
                componentName="VegaLiteChart",
                componentState={"specId": "parallel_coordinates"}
            ),
            ComponentLayoutType(
                type="component",
                className=None,
                componentName="VegaLiteChart",
                componentState={"specId": "spider_chart"}
            ),
        ]
    )

    row4 = RowLayoutType(
        type="row",
        className=None,
        content=[
            ComponentLayoutType(
                type="component",
                className=None,
                componentName="HelloView",
                componentState={"specId": "pareto_line_chart"}
            ),
            ComponentLayoutType(
                className=None,
                type="component",
                componentName="VegaLiteChart",
                componentState={"specId": "scatter_matrix"}
            ),
        ]
    )
    return ColLayoutType(
        type="col",
        className=None,
        content=[
            row1,
            row2,
            row3,
            row4

        ]
    )

@app.get("/initialize")
def initialize():
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

    # 1. Batch-wise Performance Summary (Line Plot with Points)
    performance_summary = df.groupby('Batch').agg(
        min_performance=('Performance', 'min'),
        max_performance=('Performance', 'max'),
        avg_performance=('Performance', 'mean'),
        min_time=('Time', 'min'),
        max_time=('Time', 'max'),
        avg_time=('Time', 'mean'),
        failure_rate=('FailureReason', lambda x: x.notna().mean())
    ).reset_index()

    performance_chart = alt.Chart(performance_summary).transform_fold(
        ['min_performance', 'max_performance', 'avg_performance']
    ).mark_line(point=True).encode(
        x='Batch:N',
        y='value:Q',
        color='key:N',
        tooltip=['Batch:N', 'key:N', 'value:Q']
    ).properties(
        title='Batch-wise Performance Summary'
    )

    # 2. Failure Rates and Reasons (Stacked Bar Chart)
    failure_chart = alt.Chart(df).mark_bar().encode(
        x='Batch:N',
        y='count():Q',
        color='FailureReason:N',
        tooltip=['Batch', 'FailureReason', 'count()']
    ).properties(
        title='Failure Rates and Reasons by Batch'
    )

    # 3. Pareto Calculation for Population Level (Scatter Plot)
    pareto_chart = alt.Chart(df).mark_circle(size=60).encode(
        x='Performance:Q',
        y='ConstraintSatisfaction:Q',
        color='Batch:N',
        tooltip=['Batch', 'Run', 'Performance', 'ConstraintSatisfaction', 'ParetoScore']
    ).properties(
        title='Pareto Front Analysis'
    )

    # 4. Multi-optimization Comparison (Scatter Plot with Horizontal Threshold Line)
    comparison_chart = alt.Chart(df).mark_circle(size=60).encode(
        x='Performance:Q',
        y='Time:Q',
        color='Batch:N',
        tooltip=['Batch', 'Run', 'Performance', 'Time', 'ConstraintSatisfaction', 'FailureReason']
    ).properties(
        title='Multi-optimization Comparison'
    )

    # Add a horizontal line for a time threshold (e.g., max acceptable time)
    threshold_line = alt.Chart(pd.DataFrame({'y': [25]})).mark_rule(color='red').encode(y='y:Q')

    comparison_chart_with_line = comparison_chart + threshold_line

    # 5. Heatmap of Failure Rates by Batch and Run (Heatmap)
    heatmap = alt.Chart(df).mark_rect().encode(
        x='Batch:N',
        y='Run:O',
        color='FailureReason:N',
        tooltip=['Batch', 'Run', 'FailureReason']
    ).properties(
        title='Heatmap of Failures by Batch and Run'
    )

    # 6. Parallel Coordinates Plot for Performance Metrics (Parallel Coordinates)
    parallel_coordinates = alt.Chart(df).transform_window(
        window=[{'op': 'rank', 'as': 'rank'}],
        sort=[{'field': 'Batch'}, {'field': 'Run'}]
    ).transform_fold(
        ['Performance', 'Time', 'ConstraintSatisfaction', 'ParetoScore']
    ).mark_line().encode(
        x='key:N',
        y='value:Q',
        color='Batch:N',
        detail='rank:N',
        tooltip=['Batch', 'Run', 'key:N', 'value:Q']
    ).properties(
        title='Parallel Coordinates Plot for Performance Metrics'
    )

    # 7. Spider Chart for Batch-wise Summary (Alternative to Parallel Coordinates)
    # Note: Altair doesn't directly support spider charts, but a radar chart can be mimicked with line plots.
    spider_data = performance_summary.melt(id_vars='Batch', value_vars=['min_performance', 'max_performance', 'avg_performance'])
    spider_chart = alt.Chart(spider_data).mark_line(point=True).encode(
        theta=alt.Theta('variable:N', sort=['min_performance', 'max_performance', 'avg_performance']),
        radius=alt.Radius('value:Q', scale=alt.Scale(type='sqrt', zero=True, rangeMin=20)),
        color='Batch:N',
        tooltip=['Batch', 'variable', 'value']
    ).properties(
        title='Spider Chart for Batch-wise Summary (Mimic)'
    )

    # 8. Line Plot for Pareto Score over Batches
    pareto_line_chart = alt.Chart(df).mark_line(point=True).encode(
        x='Batch:N',
        y='ParetoScore:Q',
        color='Batch:N',
        tooltip=['Batch', 'Run', 'ParetoScore']
    ).properties(
        title='Pareto Score over Batches'
    )

    # 9. Scatter Matrix to Explore Relationships (Scatter Matrix)
    scatter_matrix = alt.Chart(df).transform_fold(
        ['Performance', 'Time', 'ConstraintSatisfaction', 'ParetoScore'],
    ).mark_point().encode(
        x=alt.X('value:Q', scale=alt.Scale(zero=False)),
        y=alt.Y('value:Q', scale=alt.Scale(zero=False)),
        color='Batch:N',
        facet=alt.Facet('key:N', columns=2),
        tooltip=['Batch', 'Run', 'key:N', 'value:Q']
    ).properties(
        title='Scatter Matrix for Relationship Exploration'
    )

    # Combine and display all charts
    combined_chart = alt.vconcat(
        performance_chart, 
        failure_chart, 
        pareto_chart, 
        comparison_chart_with_line, 
        heatmap, 
        parallel_coordinates, 
        pareto_line_chart,
        scatter_matrix
    ).configure_title(
        fontSize=20,
        anchor='start',
        color='gray'
    )

    addChartSpec("performance_chart", performance_chart)
    addChartSpec("failure_chart", failure_chart)
    addChartSpec("pareto_chart", pareto_chart)
    addChartSpec("comparison_chart_with_line", comparison_chart_with_line)
    addChartSpec("heatmap", heatmap)
    addChartSpec("parallel_coordinates", parallel_coordinates)
    addChartSpec("spider_chart", spider_chart)
    addChartSpec("pareto_line_chart", pareto_line_chart)
    addChartSpec("scatter_matrix", scatter_matrix)

    return DashboardResponse(layout=getLayout(), vegaSpecs=vegaSpecs)
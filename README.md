# dash-template-rendering

> Develop Dash layout with ease, using html template files.

![PyPI - Licence](https://img.shields.io/pypi/l/dash-template-rendering)
[![Current version on PyPI](https://img.shields.io/pypi/v/dash-template-rendering)](https://pypi.org/project/dash-template-rendering/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dash-template-rendering.svg?color=dark-green)](https://pypi.org/project/dash-template-rendering/)
[![codecov](https://codecov.io/gh/pschleiter/dash-template-rendering/branch/main/graph/badge.svg?token=148H4RN9NN)](https://codecov.io/gh/pschleiter/dash-template-rendering)

dash_template_rendering is a simple [Dash](https://dash.plotly.com/) Python extension for rendering html content
for the dashboard with [Jinja2](https://palletsprojects.com/p/jinja/). The rendered content can be used for the `dash.layout`
and the return of callbacks.

## Installation

```
$ pip install dash-template-rendering
```

## Examples

### Minimal Dash App

The [minimal Dash App](https://dash.plotly.com/minimal-app) implemented with the dash-template-rendering package.

```python
from dash import Dash, dcc, callback, Output, Input
from dash_template_rendering import TemplateRenderer, render_dash_template_string
import plotly.express as px
import pandas as pd

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)

app = Dash(__name__)
TemplateRenderer(dash=app)

app.layout = render_dash_template_string(
    """
<div>
    <h1 style="text-align:center;">Title of Dash App</h1>
    {{ dropdown | plotly }}
    {{ graph | plotly }}
</div>
""",
    dropdown=dcc.Dropdown(df.country.unique(), "Canada", id="dropdown-selection"),
    graph=dcc.Graph(id="graph-content"),
)


@callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x="year", y="pop")


if __name__ == "__main__":
    app.run_server(debug=True)
```

### Advanced Example

The full potential of this extension is applied, when combined with an CSS framework (e.g. [Bootstrap](https://getbootstrap.com/)).

The [Iris k-means clustering Dash App](http://dash-bootstrap-components.opensource.faculty.ai/examples/iris/) implemented with the dash-template-rendering package.

```python
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, dcc
from dash_template_rendering import TemplateRenderer, render_dash_template_string
from sklearn import datasets
from sklearn.cluster import KMeans

iris_raw = datasets.load_iris()
iris = pd.DataFrame(iris_raw["data"], columns=iris_raw["feature_names"])

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
TemplateRenderer(dash=app)

dropdown_x_variable = dcc.Dropdown(
    id="x-variable",
    options=[{"label": col, "value": col} for col in iris.columns],
    value="sepal length (cm)",
)
dropdown_y_variable = dcc.Dropdown(
    id="y-variable",
    options=[{"label": col, "value": col} for col in iris.columns],
    value="sepal width (cm)",
)
input_cluster_count = dbc.Input(id="cluster-count", type="number", value=3)

graph_cluster = dcc.Graph(id="cluster-graph")


app.layout = render_dash_template_string(
    """
        <div class="container d-fluid">
            <h1>Iris k-means clustering</h1>
            <hr>
            <div class="align-items-center row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <label class="form-label">X variable</label>
                            {{ dropdown_x_variable | plotly }}
                            <label class="form-label">Y variable</label>
                            {{ dropdown_y_variable | plotly }}
                            <label class="form-label">Cluster count</label>
                            {{ input_cluster_count | plotly }}
                        </div>
                    </div>
                </div>
                <div class="col-md-8">
                    {{ graph_cluster | plotly }}
                </div>
            </div>
        </div>
    """,
    dropdown_x_variable=dropdown_x_variable,
    dropdown_y_variable=dropdown_y_variable,
    input_cluster_count=input_cluster_count,
    graph_cluster=graph_cluster,
)


@app.callback(
    Output("cluster-graph", "figure"),
    [
        Input("x-variable", "value"),
        Input("y-variable", "value"),
        Input("cluster-count", "value"),
    ],
)
def make_graph(x, y, n_clusters):
    # minimal input validation, make sure there's at least one cluster
    km = KMeans(n_clusters=max(n_clusters, 1), n_init=10)
    df = iris.loc[:, [x, y]]
    km.fit(df.values)
    df["cluster"] = km.labels_

    centers = km.cluster_centers_

    data = [
        go.Scatter(
            x=df.loc[df.cluster == c, x],
            y=df.loc[df.cluster == c, y],
            mode="markers",
            marker={"size": 8},
            name="Cluster {}".format(c),
        )
        for c in range(n_clusters)
    ]

    data.append(
        go.Scatter(
            x=centers[:, 0],
            y=centers[:, 1],
            mode="markers",
            marker={"color": "#000", "size": 12, "symbol": "diamond"},
            name="Cluster centers",
        )
    )

    layout = {"xaxis": {"title": x}, "yaxis": {"title": y}}

    return go.Figure(data=data, layout=layout)


# make sure that x and y values can't be the same variable
def filter_options(v):
    """Disable option v"""
    return [{"label": col, "value": col, "disabled": col == v} for col in iris.columns]


# functionality is the same for both dropdowns, so we reuse filter_options
app.callback(Output("x-variable", "options"), [Input("y-variable", "value")])(
    filter_options
)
app.callback(Output("y-variable", "options"), [Input("x-variable", "value")])(
    filter_options
)


if __name__ == "__main__":
    app.run_server(debug=True, port=8888)

```

## License

This project is licensed under the MIT License (see the `LICENSE` file for
details).

# dash-template-rendering
![PyPI - Licence](https://img.shields.io/pypi/l/dash-template-rendering)
[![Current version on PyPI](https://img.shields.io/pypi/v/dash-template-rendering)](https://pypi.org/project/dash-template-rendering/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dash-template-rendering.svg?color=dark-green)](https://pypi.org/project/dash-template-rendering/)
[![Build Status](https://github.com/pschleiter/dash-template-rendering/workflows/build/badge.svg)](https://github.com/pschleiter/dash-template-rendering/actions)
[![codecov](https://codecov.io/gh/pschleiter/dash-template-rendering/branch/main/graph/badge.svg?token=148H4RN9NN)](https://codecov.io/gh/pschleiter/dash-template-rendering)

Dash Python extention for rendering Jinja2 templates.


## Simple example

Based on the [dash minimal app](https://dash.plotly.com/minimal-app).

    from dash import Dash, html, dcc, callback, Output, Input
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
        <h3>You can use all jinja2 features too.</h3>
        <ul>
        {% for i in [1,2,3] %}
            <li>Item {{ i }}</li>
        {% endfor %}
        </ul>
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

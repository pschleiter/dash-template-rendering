import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dcc
from dash_template_rendering import TemplateRenderer, render_dash_template_string

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

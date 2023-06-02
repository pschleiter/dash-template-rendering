import pytest
from flask import Flask
from dash import Dash, html
from dash_template_rendering import TemplateRenderer


@pytest.fixture
def app() -> Flask:
    app = Flask(import_name="test")
    app.config.from_mapping({"TESTING": True})

    yield app


@pytest.fixture(autouse=True)
def dashboard(app) -> Dash:
    dashboard = Dash(server=app)
    dashboard.layout = html.Div()

    return dashboard


@pytest.fixture(autouse=True)
def template_renderer(dashboard) -> TemplateRenderer:
    return TemplateRenderer(dash=dashboard)


@pytest.fixture()
def client(app):
    context = app.test_request_context()
    context.push()

    with app.test_client() as client:
        yield client

    context.pop()


@pytest.fixture
def template_string():
    return """
<div class="container">
    <div class="row">
        <div class="col-3 col-md-6">
            first row - small column
        </div>
        <div class="col-9">
            first row - large column
        </div>
    </div>
    <!-- HTML comment -->
    {{ dash_row|plotly }}
</div>
"""


@pytest.fixture
def dash_row():
    return html.Div(
        className="row",
        children=[
            html.Div(
                className="col-9 col-md-6",
                children="second row - large column",
            ),
            html.Div(
                className="col-3",
                children="second row - small column",
            ),
        ],
    )


@pytest.fixture
def template_dash(dash_row):
    return html.Div(
        className="container",
        children=[
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="col-3 col-md-6",
                        children="first row - small column",
                    ),
                    html.Div(
                        className="col-9",
                        children="first row - large column",
                    ),
                ],
            ),
            dash_row,
        ],
    )


@pytest.fixture
def template_json():
    return {
        "props": {
            "className": "container",
            "children": [
                {
                    "props": {
                        "className": "row",
                        "children": [
                            {
                                "props": {
                                    "className": "col-3 col-md-6",
                                    "children": ["first row - small column"],
                                },
                                "type": "Div",
                                "namespace": "dash_html_components",
                            },
                            {
                                "props": {
                                    "className": "col-9",
                                    "children": ["first row - large column"],
                                },
                                "type": "Div",
                                "namespace": "dash_html_components",
                            },
                        ],
                    },
                    "type": "Div",
                    "namespace": "dash_html_components",
                },
                {
                    "props": {
                        "children": [
                            {
                                "props": {
                                    "children": "second row - large column",
                                    "className": "col-9 col-md-6",
                                },
                                "type": "Div",
                                "namespace": "dash_html_components",
                            },
                            {
                                "props": {
                                    "children": "second row - small column",
                                    "className": "col-3",
                                },
                                "type": "Div",
                                "namespace": "dash_html_components",
                            },
                        ],
                        "className": "row",
                    },
                    "type": "Div",
                    "namespace": "dash_html_components",
                },
            ],
        },
        "type": "Div",
        "namespace": "dash_html_components",
    }

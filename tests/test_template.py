import pytest
import json
from bs4 import BeautifulSoup
from flask import render_template_string
import plotly

from dash_template_rendering import render_dash_template_string


@pytest.mark.usefixtures("client")
def test_empty_template():
    with pytest.raises(ValueError, match="Empty template in use. Please remove."):
        template = render_dash_template_string(source="")


@pytest.mark.usefixtures("client")
def test_template(template_string, dash_row, template_json):
    template = render_dash_template_string(
        source=render_template_string(template_string, dash_row=dash_row)
    )

    assert (
        json.loads(plotly.io.json.to_json_plotly(template.to_plotly_json()))
        == template_json
    )


@pytest.mark.usefixtures("client")
def test_render_dash_template_string(template_string, dash_row, template_json):
    template = render_dash_template_string(template_string, dash_row=dash_row)

    assert (
        json.loads(plotly.io.json.to_json_plotly(template.to_plotly_json()))
        == template_json
    )

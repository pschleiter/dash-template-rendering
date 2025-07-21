from operator import attrgetter
import pytest
import json

import plotly
from dash import html

from dash_template_rendering import render_dash_template, render_dash_template_string


@pytest.mark.usefixtures('client')
def test_render_template(app, template_string, dash_row, template_json):
    template = render_dash_template(
        template_name_or_list=app.jinja_env.from_string(template_string),
        dash_row=dash_row,
    )

    assert (
        json.loads(plotly.io.json.to_json_plotly(template.to_plotly_json()))
        == template_json
    )


@pytest.mark.usefixtures('client')
def test_render_dash_template_string(template_string, dash_row, template_json):
    template = render_dash_template_string(template_string, dash_row=dash_row)

    assert (
        json.loads(plotly.io.json.to_json_plotly(template.to_plotly_json()))
        == template_json
    )


@pytest.mark.usefixtures('client')
def test_empty_template():
    with pytest.raises(
        ValueError,
        match='Empty template in use. Please remove.',
    ):
        render_dash_template_string(source='')


@pytest.mark.usefixtures('client')
def test_two_main_tags_warning_template():
    with pytest.warns(
        UserWarning,
        match=(
            'Template Tag has more than one main tag, '
            'which is not supported. '
            'Only the first tag is used.'
        ),
    ):
        template = render_dash_template_string(
            source="""
                <div id="tag1"></div>
                <div id="tag2"></div>
            """
        )

    assert isinstance(template, html.Div)
    assert attrgetter('id')(template) == 'tag1'


@pytest.mark.usefixtures('client')
def test_skip_unknown_tags_template():
    with pytest.raises(
        TypeError,
        match=(
            'Generating dash component from html tag failed. '
            'No corresponding dash component found for html tag "unknown_tag".'
        ),
    ):
        render_dash_template_string(
            source="""
                <unknown_tag></unknown_tag>
            """
        )

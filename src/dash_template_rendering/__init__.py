__version__ = "0.0.1-alpha"

import json
import typing
import inspect
import warnings
import textwrap
import importlib

import bs4

from flask import render_template, render_template_string
from markupsafe import Markup

import plotly
import dash
from dash.development.base_component import Component


def to_json_plotly_tag(component: Component):
    return Markup(f"<plotly>{plotly.io.json.to_json_plotly(component)}</plotly>")


DASH_TAGS_MAPPING = dict(
    map(lambda x: (x[0].lower(), x[1]), inspect.getmembers(dash.html, inspect.isclass))
)


def _parse_template(template_string: str) -> Component:
    soup = bs4.BeautifulSoup(template_string, "html.parser")
    plotly_elements = _parse_elements(html_elements=soup.contents)
    if len(plotly_elements) >= 1:
        if len(plotly_elements) > 1:
            warnings.warn(
                "Template Tag has more than one main tag, which is not supported. "
                "Only the first tag is used."
            )
        return plotly_elements[0]
    else:
        raise ValueError("Empty template in use. Please remove.")


def _parse_elements(
    html_elements: typing.Iterable[bs4.PageElement],
) -> list[str | dict | Component]:
    plotly_elements = []
    for child in html_elements:
        if isinstance(child, bs4.element.Tag):
            tag = _parse_tag(child)
            if tag is not None:
                plotly_elements.append(tag)
        elif isinstance(child, bs4.element.NavigableString):
            if isinstance(child, bs4.element.PreformattedString):
                continue
            elif (
                isinstance(child, bs4.element.Stylesheet)
                or isinstance(child, bs4.element.Script)
                or isinstance(child, bs4.element.TemplateString)
                or isinstance(child, bs4.element.RubyTextString)
            ):
                warnings.warn(
                    f"Node type {type(child)} is not supported in templates yet. Node will be skipped."
                )
                continue
            else:
                text = _parse_navigable_string(child)
                if text is not None:
                    plotly_elements.append(text)
        else:
            warnings.warn(
                f"Node type {type(child)} is not supported in templates yet. Node will be skipped."
            )
            continue

    return plotly_elements


def _parse_dash_json(data: dict) -> Component:
    component_class = getattr(importlib.import_module(data["namespace"]), data["type"])
    element = component_class(**data["props"])
    if hasattr(element, "children") and element.children is not None:
        if isinstance(element.children, dict):
            element.children = [element.children]

        if isinstance(element.children, list):
            children = []
            for child in element.children:
                children.append(_parse_dash_json(child))
            element.children = children
    return element


def _parse_tag(tag: bs4.Tag) -> dict | Component:
    if tag.name == "plotly":
        return _parse_dash_json(data=json.loads(tag.text))
    elif tag.name.lower() in DASH_TAGS_MAPPING.keys():
        component_class = DASH_TAGS_MAPPING[tag.name.lower()]
        available_properties = component_class().available_properties

        tag_attributes = tag.attrs

        tag_attributes.update(
            {k: " ".join(v) for k, v in tag_attributes.items() if isinstance(v, list)}
        )

        if "class" in tag_attributes:
            if "class_name" in available_properties:
                tag_attributes["class_name"] = tag_attributes.pop("class")
            elif "className" in available_properties:
                tag_attributes["className"] = tag_attributes.pop("class")

        children = list(filter(lambda x: x is not None, _parse_elements(tag.contents)))
        if len(children) > 0:
            tag_attributes["children"] = children

        try:
            return component_class(**tag_attributes)
        except TypeError as e:
            raise TypeError(
                f"Generating dash component from html tag failed.\nHTML Tag:\n{textwrap.indent(textwrap.shorten(tag.prettify(), width=200), '+ ')}\nDash Failure:\n{textwrap.indent(e.args[0], '+ ')}"
            )
    raise TypeError(
        f'Generating dash component from html tag failed. No corresponding dash component found for html tag "{tag.name}".'
    )


def _parse_navigable_string(navigable_string: bs4.NavigableString) -> str:
    text = navigable_string.text.strip()
    if text:
        return text
    else:
        return None


def render_dash_template(
    template_name_or_list: str | list[str], **context: typing.Any
) -> Component:
    with dash.get_app().server.app_context():
        return _parse_template(
            template_string=render_template(template_name_or_list, **context)
        )


def render_dash_template_string(source: str, **context: typing.Any) -> Component:
    with dash.get_app().server.app_context():
        return _parse_template(
            template_string=render_template_string(source, **context)
        )


class TemplateRenderer:
    def __init__(self, dash: dash.Dash | None = None) -> None:
        self._dash = None

        if dash is not None:
            self.init_dash(dash=dash)

    def init_dash(self, dash: dash.Dash) -> None:
        self._dash = dash
        dash.server.jinja_env.filters["plotly"] = to_json_plotly_tag

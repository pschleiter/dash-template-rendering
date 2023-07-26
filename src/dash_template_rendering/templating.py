import importlib
import inspect
import json
import re
import textwrap
import typing
import warnings

import bs4
import dash
from dash.development.base_component import Component
from flask import render_template, render_template_string
from jinja2 import Template

DASH_TAGS_MAPPING = dict(
    map(
        lambda x: (x[0].lower(), x[1]),
        inspect.getmembers(dash.html, inspect.isclass),
    )
)

NAMESPACE_MAPPING = {
    "dash_html_components": "dash.html",
    "dash_core_components": "dash.dcc",
}


def _parse_template(template_string: str) -> Component:
    soup = bs4.BeautifulSoup(template_string, "html.parser")
    plotly_elements = _parse_elements(html_elements=soup.contents)
    if len(plotly_elements) >= 1:
        if len(plotly_elements) > 1:
            warnings.warn(
                "Template Tag has more than one main tag, "
                "which is not supported. "
                "Only the first tag is used."
            )
        return plotly_elements[0]
    else:
        raise ValueError("Empty template in use. Please remove.")


def _parse_elements(
    html_elements: typing.Iterable[bs4.PageElement],
) -> typing.List[Component]:
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
                    f"Node type {type(child)} is not supported "
                    "in templates yet. Node will be skipped."
                )
                continue
            else:
                text = _parse_navigable_string(child)
                if text is not None:
                    plotly_elements.append(text)
        else:
            warnings.warn(
                f"Node type {type(child)} is not supported "
                "in templates yet. Node will be skipped."
            )
            continue

    return plotly_elements


def _resolve_namespace(namespace: str) -> str:
    if namespace in NAMESPACE_MAPPING.keys():
        return NAMESPACE_MAPPING[namespace]
    return namespace


def _parse_dash_json(data: dict) -> Component:
    component_class = getattr(
        importlib.import_module(_resolve_namespace(data["namespace"])),
        data["type"],
    )
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


def _parse_tag(tag: bs4.Tag) -> Component:
    if tag.name == "plotly":
        return _parse_dash_json(data=json.loads(tag.text))
    elif tag.name.lower() in DASH_TAGS_MAPPING.keys():
        component_class = DASH_TAGS_MAPPING[tag.name.lower()]
        available_properties = component_class().available_properties

        tag_attributes = tag.attrs

        tag_attributes.update(
            {k: " ".join(v) for k, v in tag_attributes.items() if isinstance(v, list)}
        )

        _apply_special_dash_attribute_naming(
            available_properties=available_properties, tag_attributes=tag_attributes
        )

        children = list(
            filter(lambda x: x is not None, _parse_elements(tag.contents)),
        )
        if len(children) > 0:
            tag_attributes["children"] = children

        try:
            return component_class(**tag_attributes)
        except TypeError as e:
            pretty_tag = textwrap.indent(
                textwrap.shorten(tag.prettify(), width=200), "+ "
            )
            raise TypeError(
                f"Generating dash component from html tag failed.\n"
                f"HTML Tag:\n"
                f"{pretty_tag}\n"
                f"Dash Failure:\n{textwrap.indent(e.args[0], '+ ')}"
            )
    raise TypeError(
        f"Generating dash component from html tag failed. "
        f'No corresponding dash component found for html tag "{tag.name}".'
    )


def _apply_special_dash_attribute_naming(available_properties, tag_attributes):
    for dash_name in available_properties:
        if dash_name.lower() in tag_attributes:
            tag_attributes[dash_name] = tag_attributes.pop(dash_name.lower())

    if "class_name" in available_properties and "class" in tag_attributes:
        tag_attributes["class_name"] = tag_attributes.pop("class")
    if "className" in available_properties and "class" in tag_attributes:
        tag_attributes["className"] = tag_attributes.pop("class")
    if "htmlFor" in available_properties and "for" in tag_attributes:
        tag_attributes["htmlFor"] = tag_attributes.pop("for")

    if "style" in tag_attributes and "style" in available_properties:
        styles = {}
        for style in tag_attributes["style"].split(";"):
            key, _, value = style.partition(":")
            key = re.sub(r"\-(\w)", lambda y: y.group(1).upper(), key).strip()
            value = value.strip()
            if len(key) == 0:
                continue

            styles[key] = value

        tag_attributes["style"] = styles


def _parse_navigable_string(navigable_string: bs4.NavigableString) -> str:
    text = navigable_string.text.strip()
    if text:
        return text
    else:
        return None


def render_dash_template(
    template_name_or_list: typing.Union[
        str, Template, typing.List[typing.Union[str, Template]]
    ],
    **context: typing.Any,
) -> Component:
    """Render a template by name with the given context.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.
    :return: The render html content expressed as Dash ``Component``.
    """
    with dash.get_app().server.app_context():
        return _parse_template(
            template_string=render_template(template_name_or_list, **context)
        )


def render_dash_template_string(
    source: str,
    **context: typing.Any,
) -> Component:
    """Render a template from the given source string with the given context.

    :param source: The source code of the template to render.
    :param context: The variables to make available in the template.
    :return: The render html content expressed as Dash ``Component``.
    """
    with dash.get_app().server.app_context():
        return _parse_template(
            template_string=render_template_string(source, **context)
        )

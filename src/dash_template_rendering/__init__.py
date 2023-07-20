"""
dash_template_rendering is a simple Dash Python extension for rendering html content
for the dashboard with jinja2. The rendered content can be used for the ``dash.layout``
and the return of callbacks.
"""
from .template_renderer import TemplateRenderer  # noqa: F401
from .templating import render_dash_template, render_dash_template_string  # noqa: F401

__version__ = "0.0.1-beta2"

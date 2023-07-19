import typing

import dash
import plotly
from dash.development.base_component import Component
from markupsafe import Markup


def to_json_plotly_tag(component: Component):
    return Markup(
        f"<plotly>{plotly.io.json.to_json_plotly(component)}</plotly>",
    )


class TemplateRenderer:
    """Extension class for rendering html content with jinja2 templates.

    Initialize the extension::

        from dash import Dash
        from dash_template_rendering import TemplateRenderer

        app = Dash(__name__)
        TemplateRenderer(dash=app)

    Or with the application factory::

        from dash import Dash
        from dash_template_rendering import TemplateRenderer

        template_renderer = TemplateRenderer()

        def create_app():
            app = Dash(__name__)
            template_renderer.init_dash(dash=app)

    :param dash: Call :meth:`init_dash` on this Dash application now.
    """

    def __init__(self, dash: typing.Optional[dash.Dash] = None) -> None:
        self._dash = None

        if dash is not None:
            self.init_dash(dash=dash)

    def init_dash(self, dash: dash.Dash) -> None:
        """Initialize a dash application fo use with this extension instance. This must be
        called before the first templates are rendered.

        :param dash: The Dash application to initialize.
        """
        self._dash = dash
        dash.server.jinja_env.filters["plotly"] = to_json_plotly_tag

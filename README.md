# dash-template-rendering
Dash Python extention for rendering Jinja2 templates.


## Simple example

    from dash import Dash, html
    from dash_template_rendering import TemplateRenderer, render_dash_template_string

    app = Dash(name=__name__)
    TemplateRenderer(dash=app)

    app.layout = render_dash_template_string(
        """
    <div>
        <h1>Hello to dash-template-rendering</h1>
        <h3>You can use all jinja2 features</h3>
        <ul>
        {% for i in [1,2,3] %}
            <li>Item {{ i }}</li>
        {% endfor %}
        </ul>
    </div>
    """
    )
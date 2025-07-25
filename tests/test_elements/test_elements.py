from functools import partial
from operator import attrgetter
from hypothesis import given
from hypothesis.strategies import from_regex
from hypothesis.provisional import urls
import pytest

from dash_template_rendering import render_dash_template_string


policy = partial(from_regex, regex=r'[a-zA-Z0-9_\-]+', fullmatch=True)

global_attributes = dict(
    accesskey=policy(),
    className=policy(),
    contenteditable=policy(),
    dir=policy(),
    draggable=policy(),
    hidden=policy(),
    id=policy(),
    lang=from_regex(regex=r'[a-z]{2}\-[A-Z]{2}', fullmatch=True),
    spellcheck=from_regex(regex=r'(true)|(false)', fullmatch=True),
    tabindex=from_regex(regex=r'[-]?\d+'),
    title=policy(),
)

style_attribute = [
    (
        'margin-bottom: 50px; margin-top: 25px;',
        dict(marginBottom='50px', marginTop='25px'),
    ),
    ('color: blue; font-size: 14px', dict(color='blue', fontSize='14px')),
]

TRANSLATION = {
    'hreflang': 'hrefLang',
    'referrerpolicy': 'referrerPolicy',
    'accesskey': 'accessKey',
    'contenteditable': 'contentEditable',
    'spellcheck': 'spellCheck',
    'tabindex': 'tabIndex',
    'autofocus': 'autoFocus',
    'formaction': 'formAction',
    'formenctype': 'formEncType',
    'formtarget': 'formTarget',
    'formnovalidate': 'formNoValidate',
    'formmethod': 'formMethod',
    'for': 'htmlFor',
}


@pytest.mark.usefixtures('client')
@pytest.mark.parametrize(
    'style_str,style_dict',
    style_attribute,
)
@given(
    download=from_regex(regex=r'[a-zA-Z_\-]+\.[a-z]{1,4}', fullmatch=True),
    href=urls(),
    hreflang=from_regex(regex=r'[a-z]{2}\-[A-Z]{2}', fullmatch=True),
    referrerpolicy=policy(),
    rel=policy(),
    target=policy(),
    **global_attributes,
)
def test_element_a(style_str, style_dict, **kwargs):
    element = render_dash_template_string(
        source="""
            <a
            {% for k, v in kwargs.items() %}
                {% if k == "className" %}
                    {% set k = "class" %}
                {% endif %}
                {{ k }}="{{ v }}"
            {% endfor %}
                style="{{ style }}"
            >
        """,
        style=style_str,
        kwargs=kwargs,
    )

    for key, value in kwargs.items():
        assert getattr(element, TRANSLATION.get(key, key)) == value

    assert attrgetter('style')(element) == style_dict


@pytest.mark.usefixtures('client')
@pytest.mark.parametrize(
    'style_str,style_dict',
    style_attribute,
)
@given(
    name=policy(),
    disabled=policy(),
    formenctype=policy(),
    type=policy(),
    formtarget=policy(),
    formnovalidate=policy(),
    autofocus=policy(),
    form=policy(),
    formmethod=policy(),
    formaction=policy(),
    value=policy(),
    **global_attributes,
)
def test_element_button(style_str, style_dict, **kwargs):
    element = render_dash_template_string(
        source="""
            <button
            {% for k, v in kwargs.items() %}
                {% if k == "className" %}
                    {% set k = "class" %}
                {% endif %}
                {{ k }}="{{ v }}"
            {% endfor %}
                style="{{ style }}"
            >
        """,
        style=style_str,
        kwargs=kwargs,
    )

    for key, value in kwargs.items():
        assert getattr(element, TRANSLATION.get(key, key)) == value

    assert attrgetter('style')(element) == style_dict


@pytest.mark.usefixtures('client')
@pytest.mark.parametrize(
    'style_str,style_dict',
    style_attribute,
)
@given(
    _for=policy(),
    **global_attributes,
)
def test_element_label(style_str, style_dict, **kwargs):
    keys = list(kwargs.keys())
    for k in keys:
        if k.startswith('_'):
            kwargs[k[1:]] = kwargs.pop(k)

    element = render_dash_template_string(
        source="""
            <label
            {% for k, v in kwargs.items() %}
                {% if k == "className" %}
                    {% set k = "class" %}
                {% endif %}
                {{ k }}="{{ v }}"
            {% endfor %}
                style="{{ style }}"
            >
        """,
        style=style_str,
        kwargs=kwargs,
    )

    for key, value in kwargs.items():
        assert getattr(element, TRANSLATION.get(key, key)) == value

    assert attrgetter('style')(element) == style_dict


@pytest.mark.usefixtures('client')
@pytest.mark.parametrize(
    'style_str,style_dict',
    style_attribute,
)
@given(
    **global_attributes,
)
def test_element_p(style_str, style_dict, **kwargs):
    element = render_dash_template_string(
        source="""
            <p
            {% for k, v in kwargs.items() %}
                {% if k == "className" %}
                    {% set k = "class" %}
                {% endif %}
                {{ k }}="{{ v }}"
            {% endfor %}
                style="{{ style }}"
            >
        """,
        style=style_str,
        kwargs=kwargs,
    )

    for key, value in kwargs.items():
        assert getattr(element, TRANSLATION.get(key, key)) == value

    assert attrgetter('style')(element) == style_dict

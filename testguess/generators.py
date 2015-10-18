# -*- coding: utf-8 -*-
from __future__ import absolute_import
from functools import partial
from django.template.loader import render_to_string

TEST_HEADERS_TEMPLATE = partial(render_to_string, template_name='testguess/headers.py')
TEST_STATUS_CODE_TEMPLATE = partial(render_to_string, template_name='testguess/status_code.py')
TEST_REVERSE_TEMPLATE = partial(render_to_string, template_name='testguess/reverse_url.py')
TEST_CUSTOM_USER_TEMPLATE = partial(render_to_string, template_name='testguess/custom_user.py')
TEST_USER_TEMPLATE = partial(render_to_string, template_name='testguess/user.py')
TEST_ANONYMOUS_USER_TEMPLATE = partial(render_to_string, template_name='testguess/anonymous_user.py')
TEST_HTML5_OUTPUT_TEMPLATE = partial(render_to_string, template_name='testguess/html5.py')
TEST_JSON_OUTPUT_TEMPLATE = partial(render_to_string, template_name='testguess/json.py')
TEST_CONTEXT_DATA_TEMPLATE = partial(render_to_string, template_name='testguess/context_data.py')

def generate_user_for_setup(config, context, **kwargs):
    if not config.is_authenticated:
        return TEST_ANONYMOUS_USER_TEMPLATE(context=context)
    if config.supports_custom_users:
        return TEST_CUSTOM_USER_TEMPLATE(context=context)
    else:
        return TEST_USER_TEMPLATE(context=context)


def generate_content_parsing_test(config, context, **kwargs):
    if config.is_html5 and config.supports_html5lib:
        return TEST_HTML5_OUTPUT_TEMPLATE(context=context)
    elif config.is_json:
        return TEST_JSON_OUTPUT_TEMPLATE(context=context)
    return None


def generate_context_data_test(config, context, response, **kwargs):
    if config.has_context_data:
        context2 = context.copy()
        context2['response']['context_keys'] = sorted(set(
            response.context_data.keys()
        ))
        context_types = tuple(
            (k, type(v)) for k, v in response.context_data.items()
        )
        context_imports_parts = tuple(
            (k, t.__module__, t.__name__)
            for k, t in context_types
            if hasattr(t, '__module__') and hasattr(t, '__name__')
            and t.__name__ not in ('__proxy__',)
        )
        context_imports = sorted(
            (mod, name) for k, mod, name in context_imports_parts
            if mod != '__builtin__' and name != 'type'
        )
        context_instances = sorted(
            (k, name) for k, mod, name in context_imports_parts
        )
        context2['response']['context_value_imports'] = context_imports
        context2['response']['context_values'] = context_instances
        return TEST_CONTEXT_DATA_TEMPLATE(context=context2)
    return None


def generate_status_code_test(context, **kwargs):
    return TEST_STATUS_CODE_TEMPLATE(context=context)


def generate_url_reverse_test(context, **kwargs):
    return TEST_REVERSE_TEMPLATE(context=context)

def generate_response_headers_test(context, **kwargs):
    return TEST_HEADERS_TEMPLATE(context=context)

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.test import TestCase


class GuessedTestCase(TestCase):
    """
    Generated: {{ when|date:'c' }}
    {% for config_name, config_value in config.items %}{{ config_name }}: {{ config_value }}
    {% endfor %}"""
    def setUp(self):
{% for s in setup %}{{ s }}{% endfor %}
        return None

{{ tests.reverse }}
{{ tests.status_code }}
{{ tests.headers }}
{{ tests.content_parsed }}
{{ tests.context_data }}


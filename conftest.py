# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import django
from django.conf import settings
import os


HERE = os.path.realpath(os.path.dirname(__file__))


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")
    if settings.configured and hasattr(django, 'setup'):
        django.setup()

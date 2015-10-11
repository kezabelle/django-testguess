# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.test import TestCase


class GuessedTestCase(TestCase):
    """
    Generated: 2015-10-11T17:34:13.320911
    is_html5: False
    is_ajax: False
    is_authenticated: True
    has_context_data: False
    has_template_name: False
    has_get_params: False
    supports_model_mommy: False
    supports_custom_users: True
    supports_html5lib: True
    is_get: True
    is_post: False
    """
    def setUp(self):
        from django.contrib.auth import get_user_model
        from django.utils.crypto import get_random_string
        User = get_user_model()
        username = '200@GET'
        password = get_random_string(5)
        user = User(**{User.USERNAME_FIELD: username})
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        self.user = user
        self.auth = {'username': username, 'password': password}
        self.client.login(**self.auth)

        return None

    def test_url_reversed(self):
        from django.core.urlresolvers import reverse
        url = reverse("2",
                      args=(),
                      kwargs={})
        self.assertEqual(url, "/2/")  # noqa

    def test_response_status_code(self):
        response = self.client.get('/2/')
        self.assertEqual(response.status_code, 200)

    def test_response_headers(self):
        response = self.client.get('/2/')
        self.assertEqual(response['Content-Type'], 'application/json')
        





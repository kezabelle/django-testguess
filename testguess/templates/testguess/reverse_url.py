    def test_url_reversed(self):
        from django.core.urlresolvers import reverse
        url = reverse("{{ request.resolved.view_name }}",
                      args={{ request.resolved.args|safe }},
                      kwargs={{ request.resolved.kwargs|safe }})
        self.assertEqual(url, "{{ request.path }}")  # noqa

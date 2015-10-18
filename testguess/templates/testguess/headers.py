    def test_response_headers(self):
        response = self.client.{{ request.method|lower }}('{{ request.path }}', data={{ request.data|safe }})
        {% for k, v in response.headers %}self.assertEqual(response['{{ k }}'], '{{ v }}')
        {% endfor %}

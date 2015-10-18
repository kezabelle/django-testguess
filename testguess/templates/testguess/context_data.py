    def test_templateresponse_context_data_contains_expected_keys(self):
        response = self.client.{{ request.method|lower }}('{{ request.path }}', data={{ request.data|safe }})
        expected = set({{ response.context_keys|safe }})
        in_context = set(response.context_data.keys())
        self.assertEqual(expected, in_context)

    def test_templateresponse_context_data_has_expected_types(self):
        {% for module, name in response.context_value_imports %}from {{ module }} import {{ name }}
        {% endfor %}
        response = self.client.{{ request.method|lower }}('{{ request.path }}', data={{ request.data|safe }})
        {% for k, v in response.context_values %}self.assertIsInstance(response.context_data['{{ k }}'], {{ v }})
        {% endfor %}

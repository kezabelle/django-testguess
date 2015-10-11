    def test_templateresponse_context_data(self):
        response = self.client.{{ request.method|lower }}('{{ request.path }}')
        expected = set({{ response.context_keys|safe }})
        self.assertEqual(expected, set(response.context_data.keys()))

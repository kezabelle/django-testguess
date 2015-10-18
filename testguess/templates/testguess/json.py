    def test_response_is_json(self):
        from json import loads
        response = self.client.{{ request.method|lower }}('{{ request.path }}', data={{ request.data|safe }})
        self.assertFalse(response.streaming)
        # rather than F, this will E
        content = loads(response.content)
        expected = {}  # TODO: Fill this in to make the test pass
        self.assertEqual(content, expected)


    def test_response_is_html5(self):
        from html5lib import parse
        response = self.client.{{ request.method|lower }}('{{ request.path }}', data={{ request.data|safe }})
        self.assertFalse(response.streaming)
        # rather than F, this will E
        parse(response.content)


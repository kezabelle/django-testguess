    def test_response_status_code(self):
        response = self.client.{{ request.method|lower }}('{{ request.path }}', data={{ request.data|safe }})
        self.assertEqual(response.status_code, {{ response.status_code }})

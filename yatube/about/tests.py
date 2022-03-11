from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_expected_in_desired_location(self):
        """Првоерка доступности cтатических адресов."""
        responce = {
            self.guest_client.get('/about/author/'): 200,
            self.guest_client.get('/about/tech/'): 200,
        }
        for value, expected in responce.items():
            with self.subTest(value=value):
                self.assertEqual(value.status_code, expected)

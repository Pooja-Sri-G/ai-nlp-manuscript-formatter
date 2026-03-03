from django.test import TestCase, Client
from django.urls import reverse

class RedirectionTest(TestCase):
    def test_custom_format_redirect(self):
        client = Client()
        response = client.post(reverse('format_file'), {'template': 'custom'})
        self.assertRedirects(response, reverse('format_custom'))

from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
class ProductTests(APITestCase):
    def test_detail_product(self):
        """
        Ensure we can create a new account object.
        """

        response = self.client.get('/products/7/')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Not found')
        self.assertEqual(response.data['name'] , 'Airpod 1')

    
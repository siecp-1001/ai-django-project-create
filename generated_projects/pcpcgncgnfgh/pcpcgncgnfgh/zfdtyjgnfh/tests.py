from django.test import TestCase


class BasicTests(TestCase):
    def test_basic_functionality(self):
        self.assertEqual(1 + 1, 2)

from django.test import TestCase
from datawinners.project.data_sender_helper import list_data_sender


class TestDataSenderGetter(TestCase):
    org_id = 'SLX364903'

    fixtures = ['test_data.json']

    def test_should_return_data_sender_list_by_organization_id(self):
        data_sender_list = list_data_sender(self.org_id)
        self.assertEqual(6, len(data_sender_list))

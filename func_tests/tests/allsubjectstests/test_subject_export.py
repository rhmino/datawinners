import os
import random
import tempfile
import unittest
import uuid
from django.test import Client

from nose.plugins.attrib import attr
import xlrd
from framework.base_test import HeadlessRunnerTest


@attr('functional_test')
class TestSubjectExport(HeadlessRunnerTest):

    def setUp(self):
        self.client = Client()
        self.mobile_number = self.random_number(6)
        self.create_subject()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

    def random_number(self, length):
        return ''.join(random.sample('1234567890', length))

    def test_export(self):
        resp = self.client.post('/entity/subject/export/',
                                {'subject_type': 'clinic', 'query_text': self.mobile_number})
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, resp.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        print "file is %s" % xlfile_name
        sheet = workbook.sheet_by_index(0)
        self.assertEqual(
            [u"What is the clinic's first name?",
             u"What is the clinic's last name?",
             u"What is the clinic's location?",
             u"What is the clinic's GPS co-ordinates? Latitude",
             u"What is the clinic's GPS co-ordinates? Longitude",
             u"What is the clinic's mobile telephone number?",
             u"What is the clinic's Unique ID Number?"],
            sheet.row_values(0, 0, 7))
        total_rows = sheet.nrows
        self.assertEqual([u'firstname', u'lastname', u'location', 3.0, 3.0, unicode(self.mobile_number)],
                         sheet.row_values(total_rows-1, 0, 6))
        self.assertEqual([], sheet.row_values(total_rows-1, 7))

    def create_subject(self):
        _from = "917798987116"
        _to = "919880734937"

        message = "cli firstname lastname location 3,3 %s" % self.mobile_number
        data = {"message": message, "from_msisdn": _from, "to_msisdn": _to, "message_id": uuid.uuid1().hex}
        self.client.post("/submission", data)

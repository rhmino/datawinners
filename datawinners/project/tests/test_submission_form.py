import unittest
from django.forms import ChoiceField
from mock import Mock, PropertyMock, patch
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import IntegerField, DateField, GeoCodeField, TextField
from mangrove.form_model.form_model import FormModel
from datawinners.project.models import Project
from datawinners.project.submission_form import EditSubmissionForm


class TestSubmissionForm(unittest.TestCase):
    def setUp(self):
        self.manager = Mock(spec=DatabaseManager)
        self.project = Mock(spec=Project)
        self.form_model = Mock(spec=FormModel)
        self.ddtype = Mock(spec=DataDictType)

    def test_should_set_initial_values_for_submissions_with_lower_case_question_codes(self):
        initial_dict = {'q1': 'Ans1', 'q2': 'Ans2'}
        type(self.form_model).fields = PropertyMock(
            return_value=[TextField(name="q1", code="q1", label="some", ddtype=self.ddtype),
                          TextField(name="q2", code="q2", label="some", ddtype=self.ddtype)])
        type(self.form_model).entity_question = PropertyMock(return_value=None)
        submission_form = EditSubmissionForm(self.manager, self.project, self.form_model, initial_dict)

        self.assertEquals('Ans1', submission_form.fields.get('q1').initial)
        self.assertEquals('Ans2', submission_form.fields.get('q2').initial)


    def test_should_set_initial_values_for_submissions_with_upper_case_question_codes(self):
        initial_dict = {'Q1': 'Ans1', 'Q2': 'Ans2'}
        type(self.form_model).fields = PropertyMock(
            return_value=[TextField(name="Q1", code="Q1", label="some", ddtype=self.ddtype),
                          TextField(name="Q2", code="Q2", label="some", ddtype=self.ddtype)])
        type(self.form_model).entity_question = PropertyMock(return_value=None)
        submission_form = EditSubmissionForm(self.manager, self.project, self.form_model, initial_dict)

        self.assertEquals('Ans1', submission_form.fields.get('Q1').initial)
        self.assertEquals('Ans2', submission_form.fields.get('Q2').initial)

    def test_should_create_submission_form_with_appropriate_fields(self):
        fields = [IntegerField('field_name', 'integer_field_code', 'label', Mock),
                  DateField('Date', 'date_field_code', 'date_label', 'dd.mm.yyyy', Mock),
                  GeoCodeField('', 'geo_field_code', '', Mock),
                  TextField('', 'text_field_code', '', Mock)]
        type(self.form_model).entity_question = PropertyMock(return_value=None)
        type(self.form_model).fields = PropertyMock(return_value=fields)

        submission_form_create = EditSubmissionForm(self.manager, self.project, self.form_model, {})
        expected_field_keys = ['form_code', 'integer_field_code', 'date_field_code', 'geo_field_code',
                               'text_field_code']
        self.assertListEqual(submission_form_create.fields.keys(), expected_field_keys)

    def test_entity_question_form_field_created(self):
        form_model = Mock(spec=FormModel)
        fields = [
            TextField("entity question", "eid", "what are you reporting on?", self.ddtype, entity_question_flag=True)]
        type(form_model).form_code = PropertyMock(return_value='001')
        type(form_model).fields = PropertyMock(return_value=fields)
        type(form_model).entity_question = PropertyMock(return_value=fields[0])

        with patch('datawinners.project.questionnaire_fields.EntityField.create') as create_entity_field:
            choice_field = ChoiceField(('sub1', 'sub2', 'sub3'))
            create_entity_field.return_value = {'eid': choice_field}
            submission_form = EditSubmissionForm(self.manager, self.project, form_model, {})
            self.assertEqual('eid', submission_form.short_code_question_code)
            self.assertEqual(choice_field, submission_form.fields['eid'])

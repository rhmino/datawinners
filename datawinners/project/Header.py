from collections import OrderedDict

from django.utils.translation import ugettext
from datawinners.entity.import_data import get_entity_type_info

from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.submission_headers import HeaderFactory
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from mangrove.form_model.field import DateField, GeoCodeField, FieldSet
from mangrove.utils.json_codecs import encode_json
from datawinners.project.helper import DEFAULT_DATE_FORMAT


class Header(object):
    def __init__(self, form_model):
        self._form_model = form_model
        self._header_list, self._header_type_list = zip(*self._select_header())

    @property
    def info(self):
        return {'header_list': self._header_list, 'header_name_list': repr(encode_json(self._header_list)),
                'header_type_list': repr(encode_json(self._header_type_list))}

    @property
    def header_list(self):
        return self._header_list

    @property
    def header_type_list(self):
        return self._header_type_list


    def _select_header(self):
        return filter(lambda each: each, self._prefix()) + self._fields_header()

    def _prefix(self):
        return [self._id(), self._subject_header(), self._submission_date_header(),
                self._data_sender_header()]

    def _submission_date_header(self):
        return ugettext("Submission Date"), DEFAULT_DATE_FORMAT.lower()

    def _data_sender_header(self):
        return ugettext("Data Sender"), ''

    def _subject_header(self):
        subject_type = self._form_model.entity_type[0]
        return (ugettext(subject_type).capitalize(), '')

    def _fields_header(self):
        return [(field.label, field.date_format if isinstance(field, DateField) else (
            "gps" if isinstance(field, GeoCodeField)  else "")) for field in self._form_model.fields[1:]]

    def _id(self):
        return "Submission Id", ''


class SubmissionsPageHeader():
    def __init__(self, form_model, submission_type):
        self._form_model = form_model
        self.submission_type = submission_type

    def get_column_title(self):
        header = HeaderFactory(self._form_model).create_header(self.submission_type)
        header_dict = header.get_header_field_dict()
        header_dict.pop('ds_id', None)
        unique_question_field_names = [es_unique_id_code_field_name(es_questionnaire_field_name(field.code, self._form_model.id, field.parent_field_code)) for
                                       field in
                                       self._form_model.entity_questions]
        for field_name in unique_question_field_names:
            header_dict.pop(field_name, None)
        return header_dict.values()

class AnalysisPageHeader():
    def __init__(self, form_model, dbm):
        self._form_model = form_model
        self._dbm = dbm
    
    def get_column_title(self):
        header = []
        datasender_columns = {'datasender.name': 'Data Sender Name',
                              'datasender.mobile_number': 'Data Sender Mobile Number',
                              'datasender.id': 'Data Sender ID Number',
                              'datasender.email': 'Data Sender Email',
                              'datasender.groups': 'Data Sender Groups',
                              'datasender.location': 'Data Sender Location'}
        for column_id, column_title in datasender_columns.iteritems():
            header.append({"data": column_id, "title": column_title, "defaultContent": ""})

        for field in self._form_model.fields:
            prefix = self._form_model.id + "_" + field.code + "_details"
            if field.is_entity_field:
                entity_type_info = get_entity_type_info(field.unique_id_type, self._dbm)
                for idx, val in enumerate(entity_type_info['names']):
                    header.append({"data": prefix+"."+val, "title": entity_type_info['labels'][idx],  "defaultContent": ""})
            else:
                header.append({"data": self._form_model.id+'_'+field.code, "title": field.label,  "defaultContent": ""})

        return header

class SubmissionExcelHeader():
    def __init__(self, form_model, submission_type, language='en'):
        self._form_model = form_model
        self.submission_type = submission_type
        self.language = language

    def add_datasender_id_column(self, header_dict, result):
        result.update({
            SubmissionIndexConstants.DATASENDER_ID_KEY: {
                "label": header_dict[SubmissionIndexConstants.DATASENDER_ID_KEY]}})

    def _update_with_field_meta(self, fields, result, header, parent_field_name=None, ):
        for field in fields:
            if isinstance(field, FieldSet) and field.is_group():
                self._update_with_field_meta(field.fields, result, header, field.code)
            else:
                field_name = es_questionnaire_field_name(field.code, self._form_model.id, parent_field_name)

                if result.has_key(field_name):
                    result.get(field_name).update({"type": field.type})
                    if field.type == "date":
                        result.get(field_name).update({"format": field.date_format})
                    if field.type == "field_set":
                        result.get(field_name).update({"fields": self.get_sub_fields_of(field, header),
                                                       "code": field.code,
                                                       'fieldset_type': field.fieldset_type})

    def get_columns(self):
        header = HeaderFactory(self._form_model, self.language).create_header(self.submission_type)
        header_dict = header.get_header_field_dict()
        result = OrderedDict()
        for key in header_dict:
            if key != SubmissionIndexConstants.DATASENDER_ID_KEY:
                result.update({key: {"label": header_dict[key]}})
                if key == SubmissionIndexConstants.DATASENDER_NAME_KEY: #add key column after name
                    self.add_datasender_id_column(header_dict, result)

        self._update_with_field_meta(self._form_model.fields, result, header=header)
        return result

    def get_sub_fields_of(self, field, header):
        col = OrderedDict()
        for field in field.fields:
            details = {"type": field.type, "label": field.label}
            col.update({field.code: details})
            if field.type == "date":
                details.update({"format": field.date_format})
            if field.type == 'unique_id':
                header.add_unique_id_field_in_repeat(field, col)
            if field.type == "field_set":
                details.update({"code": field.code})
                details.update({"fields" : self.get_sub_fields_of(field, header)})

        return col

from __future__ import absolute_import
import pytest
import os
from six import BytesIO
from clims.services.file_service.csv import Csv
from clims.models.file import OrganizationFile
from clims.models.file import MultiFormatFile
from sentry.testutils import TestCase
from sentry.models.file import File
from sentry_plugins.snpseq.plugin.handlers.sample_submission import ExcelParser
from commonlims.test.resources.resource_bag import read_binary_file
from commonlims.test.resources.resource_bag import prep_sample_submission_path
from commonlims.test.resources.resource_bag import prep_sample_submission_path_csv
from commonlims.test.resources.resource_bag import rml_sample_submission_path
from commonlims.test.resources.resource_bag import rml_sample_submission_path_csv


class TestSampleSubmissionParsing(TestCase):
    def _create_organization_file(self, file_path):
        name = os.path.basename(file_path)
        file_model = File.objects.create(
            name=name,
            type='substance-batch-file',
            headers=list(),
        )
        contents = read_binary_file(file_path)
        file_like_obj = BytesIO(contents)
        file_model.putfile(file_like_obj)
        return OrganizationFile(name=name, organization=self.organization, file=file_model)

    def _to_contents(self, csv):
        lst = list()
        for line in csv:
            lst.append('\t'.join([value for value in line]))
        return '\n'.join(lst)

    @pytest.mark.now
    def test_parse_prep_from_excel__sample_list_equals_prep_from_csv(self):
        # Arrange
        org_file = self._create_organization_file(prep_sample_submission_path())
        org_file = MultiFormatFile(org_file)

        # Act
        with MultiFormatFile(org_file) as wrapped_org_file:
            parser = ExcelParser(wrapped_org_file)
            parsed_csv = parser.as_csv()
            contents_from_excel = self._to_contents(parsed_csv)

        # Assert
        csv = Csv(prep_sample_submission_path_csv())
        contents_from_csv = self._to_contents(csv)
        assert contents_from_excel == contents_from_csv

    def test_parse_rml_from_excel__sample_list_equals_rml_from_csv(self):
        # Arrange
        org_file = self._create_organization_file(rml_sample_submission_path())

        # Act
        with ExcelParser(org_file) as parser:
            parsed_csv = parser.as_csv()
            contents_from_excel = self._to_contents(parsed_csv)

        # Assert
        csv = Csv(rml_sample_submission_path_csv())
        contents_from_csv = self._to_contents(csv)
        assert contents_from_excel == contents_from_csv

    def test_parse_rml_from_excel__project_code_is_ok(self):
        # Arrange
        org_file = self._create_organization_file(rml_sample_submission_path())

        # Act
        # Assert
        with ExcelParser(org_file) as parser:
            assert parser.project_code == 'XX-1111'

    def test_parser_prep_from_excel__without_calling_as_context_manager__exception(self):
        # Arrange
        org_file = self._create_organization_file(rml_sample_submission_path())
        parser = ExcelParser(org_file)

        # Act
        # Assert
        with pytest.raises(AssertionError):
            dummy = parser.project_code

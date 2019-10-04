import os
from six import BytesIO
from sentry.models.file import File
from sentry.testutils import TestCase
from sentry_plugins.snpseq.plugin.handlers import SampleSubmissionHandler
from clims.models.file import OrganizationFile
from commonlims.test.resources.resource_bag import prep_samples_xlsx_path
from commonlims.test.resources.resource_bag import read_binary_file
from commonlims.utility.test_utils import create_organization


class TestSampleSubmission(TestCase):
    def setUp(self):
        self.org = create_organization()

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
        return OrganizationFile(name=name, organization=self.org, file=file_model)

    def test_sample_prep__number_rows_and_columns_are_ok(self):
        file = self._create_organization_file(prep_samples_xlsx_path())
        handler = SampleSubmissionHandler()
        handler.handle(file_obj=file)
        # for line in handler.csv:
        #     print(line)
        rows = [line for line in handler.csv]
        assert 3 == len(rows)
        assert 28 == len(handler.csv.header)

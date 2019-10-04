from __future__ import absolute_import
import os
import tests
import StringIO
from six import BytesIO
from django.db import IntegrityError
from sentry.testutils import TestCase
from sentry.models.file import File
from clims.services.substance import substances
from clims.services.file_service.csv import Csv
from clims.models.file import OrganizationFile
from clims.models.substance import Substance
from sentry_plugins.snpseq.plugin.handlers import GemstoneSubstancesSubmission
from commonlims.utility.test_utils import create_organization
from commonlims.utility.test_utils import create_gemstone_substance_type
from commonlims.test.resources.resource_bag import gemstone_csv_path
from commonlims.test.resources.resource_bag import read_gemstone_csv


class TestSampleSubmissionCsv(TestCase):
    def setUp(self):
        self.org = create_organization()
        self.gemstone_sample_type = create_gemstone_substance_type(org=self.org)

    def _create_csv_organization_file(self):
        name = os.path.basename(gemstone_csv_path())
        file_model = File.objects.create(
            name=name,
            type='substance-batch-file',
            headers=list(),
        )
        contents = read_gemstone_csv()
        file_like_obj = BytesIO(contents)
        file_model.putfile(file_like_obj)
        return OrganizationFile(name=name, organization=self.org, file=file_model)

    def test_import_csv_here__with_6_gemstone_samples__6_sample_instances_created(self):
        csv = Csv(gemstone_csv_path())
        created_samples = []
        for line in csv:
            name = line['Sample ID']
            preciousness = line['Preciousness']
            color = line['Color']
            props = {
                'preciousness': preciousness,
                'color': color,
            }
            sample =substances.create(
                name=name, extensible_type=self.gemstone_sample_type,
                organization=self.org, properties=props)
            created_samples.append(sample)
        self.assertEqual(6, len(created_samples))

    def test_file_blob(self):
        name = os.path.basename(gemstone_csv_path())
        file_model = File.objects.create(
            name=name,
            type='substance-batch-file',
            headers=list(),
        )
        contents = read_gemstone_csv()
        file_like_obj = BytesIO(contents)
        file_model.putfile(file_like_obj)
        myfile = OrganizationFile(name=name, organization=self.org, file=file_model)
        with file_model.getfile() as src:
            for chunk in src.chunks():
                print(type(chunk))
                print(chunk)

        assert 1 == 1

    def test_investigate_getfile(self):
        myfile = self._create_csv_organization_file()
        for ix, line in enumerate(myfile.file.getfile()):
            print(line)
        assert 1 == 1

    def test_import_with_organization_file(self):
        myfile = self._create_csv_organization_file()
        csv = myfile.as_csv()
        created_samples = []
        for line in csv:
            name = line['Sample ID']
            preciousness = line['Preciousness']
            color = line['Color']
            props = {
                'preciousness': preciousness,
                'color': color,
            }
            sample =substances.create(
                name=name, extensible_type=self.gemstone_sample_type,
                organization=self.org, properties=props)
            created_samples.append(sample)
        self.assertEqual(6, len(created_samples))
        assert 'gemstone1-project1' == created_samples[0].name

    def test_run_gemstone_sample_submission_handler__with_csv__6_samples_found_in_db(self):
        handler = GemstoneSubstancesSubmission()
        sample_sub_file = self._create_csv_organization_file()
        handler.handle(sample_sub_file)
        all_samples = Substance.objects.all()
        expected_sample_names = [
            'gemstone1-project1',
            'gemstone2-project1',
            'gemstone3-project1',
            'gemstone4-project1',
            'gemstone5-project1',
            'gemstone6-project1',
        ]
        all_sample_names = [sample.name for sample in all_samples]
        assert set(expected_sample_names).issubset(set(all_sample_names))

    def test_import_same_samples_twice__integrity_error(self):
        handler = GemstoneSubstancesSubmission()
        sample_sub_file = self._create_csv_organization_file()
        with self.assertRaises(IntegrityError):
            handler.handle(sample_sub_file)
            handler.handle(sample_sub_file)

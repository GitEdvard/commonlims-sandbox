import os
import pytest
from six import BytesIO
from sentry.models.file import File
from sentry.testutils import TestCase
from sentry_plugins.snpseq.plugin.handlers import SampleSubmissionHandler
from sentry_plugins.snpseq.plugin.models import Sample
from sentry_plugins.snpseq.plugin.services.sample import SampleService
from sentry.plugins import plugins
from clims.models.file import OrganizationFile
from clims.models.substance import Substance
from clims.handlers import HandlerContext
from clims.handlers import SubstancesSubmissionHandler
from clims.services.application import ApplicationService
from clims.services.extensible import ExtensibleTypeNotRegistered
from commonlims.test.resources.resource_bag import prep_samples_xlsx_path
from commonlims.test.resources.resource_bag import read_binary_file


class TestSampleSubmission(TestCase):
    def setUp(self):
        self.handler_context = HandlerContext(organization=self.organization)
        self.register_extensible(Sample)


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

    @pytest.mark.skip('csv prop removed, save for dimension is written here')
    def test_sample_prep__number_rows_and_columns_are_ok(self):
        # Arrange
        file = self._create_organization_file(prep_samples_xlsx_path())
        handler = SampleSubmissionHandler(context=self.handler_context, app=self.app)

        # Act
        handler.handle(file_obj=file)

        # Assert
        rows = [line for line in handler.csv]
        assert 3 == len(rows)
        assert 28 == len(handler.csv.header)

    def test_sample_prep__3_samples_are_created(self):
        # Arrange
        file = self._create_organization_file(prep_samples_xlsx_path())
        handler = SampleSubmissionHandler(context=self.handler_context, app=self.app)

        # Act
        handler.handle(file_obj=file)

        # Assert
        expected = [
            'sample1',
            'sample2',
            'sample3',
        ]
        all_samples = Substance.objects.all()
        sample_names = [s.name for s in all_samples]
        assert set(expected).issubset(set(sample_names))

    def test_sample_prep__3_concentration_values_ok_fetched_from_substance_type(self):
        # Arrange
        file = self._create_organization_file(prep_samples_xlsx_path())
        handler = SampleSubmissionHandler(context=self.handler_context, app=self.app)

        # Act
        handler.handle(file_obj=file)

        # Assert
        expected = {
            'sample1': 100,
            'sample2': 10,
            'sample3': 10,
        }
        all_substances = Substance.objects.all()
        sample_concentrations = dict()
        for sub in all_substances:
            versioned = sub.versions.get(latest=True)
            props = versioned.properties.all()
            prop_dict = {prop.extensible_property_type.name: prop.value
                         for prop in props}
            conc = prop_dict['concentration']
            sample_concentrations[sub.name] = conc
        assert expected == sample_concentrations

    def test_sample_prep__with_direct_call_to_handler__3_concentration_values_ok(self):
        # Arrange
        file = self._create_organization_file(prep_samples_xlsx_path())
        handler = SampleSubmissionHandler(context=self.handler_context, app=self.app)

        # Act
        handler.handle(file_obj=file)

        # Assert
        expected = {
            'sample1': 100,
            'sample2': 10,
            'sample3': 10,
        }
        samples = SampleService(self.app)
        all_samples = samples.all()
        conc_dict = dict()
        for sample in all_samples:
            conc_dict[sample.name] = sample.concentration

        assert expected == conc_dict

    def test_sample_service__with_new_app_instance__exception(self):
        # Arrange
        s = Sample(name='sample1', organization=self.organization)
        s.save()
        new_app_instance = ApplicationService()
        samples = SampleService(new_app_instance)

        # Act
        # Assert
        with pytest.raises(ExtensibleTypeNotRegistered):
            samples.all()

    def test_sample_prep__with_use_of_load_file__3_concentration_values_ok(self):
        # Arrange
        contents = read_binary_file(prep_samples_xlsx_path())
        fileobj = BytesIO(contents)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fileobj)

        # Assert
        expected = {
            'sample1': 100,
            'sample2': 10,
            'sample3': 10,
        }
        samples = SampleService(self.app)
        all_samples = samples.all()
        conc_dict = dict()
        for sample in all_samples:
            conc_dict[sample.name] = sample.concentration

        assert expected == conc_dict

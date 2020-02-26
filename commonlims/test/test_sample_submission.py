import os
import pytest
import logging
from six import BytesIO
from sentry.models.file import File
from sentry.testutils import TestCase
from sentry_plugins.snpseq.plugin.models import PrepSample
from sentry_plugins.snpseq.plugin.models import RmlSample
from sentry_plugins.snpseq.plugin.models import Pool
from sentry_plugins.snpseq.plugin.models import Plate96
from sentry_plugins.snpseq.plugin.services.container import ContainerRepository
from sentry_plugins.snpseq.plugin.handlers.sample_submission import SampleSubmissionPrep
from sentry_plugins.snpseq.plugin.handlers.sample_submission import SampleSubmissionHandler
from sentry_plugins.snpseq.plugin.handlers.sample_submission import ContentsBag
from sentry.plugins import plugins
from clims.models.file import OrganizationFile
from clims.models.substance import Substance
from clims.handlers import HandlerContext
from clims.handlers import SubstancesSubmissionHandler
from clims.services.file_service.csv import Csv
from clims.services.application import ioc
from commonlims.test.resources.resource_bag import prep_sample_submission_path
from commonlims.test.resources.resource_bag import prep_sample_submission_path_csv
from commonlims.test.resources.resource_bag import rml_sample_submission_path_csv
from commonlims.test.resources.resource_bag import read_binary_file
from clims.models.container import ContainerType


class TestSampleSubmission(TestCase):
    @pytest.fixture(scope='session', autouse=True)
    def monkey_patch_file_parser_to_csv(self):
        SampleSubmissionHandler._fetch_file_contents = \
            lambda selff, file_obj: ReplaceWith.contents_bag

    def setUp(self):
        self.handler_context = HandlerContext(organization=self.organization)
        self.register_extensible(PrepSample)
        self.register_extensible(RmlSample)
        self.register_extensible(Pool)
        self.register_extensible(Plate96)
        logger = logging.getLogger('clims.files')
        logger.setLevel(logging.CRITICAL)

    def _create_plate96(self):
        ct = ContainerType(name='Plate96')
        ct.rows = 8
        ct.cols = 12
        ct.save()

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
        file = self._create_organization_file(prep_sample_submission_path())
        handler = SampleSubmissionHandler(context=self.handler_context, app=self.app)

        # Act
        handler.handle(multi_format_file=file)

        # Assert
        rows = [line for line in handler.csv]
        assert 3 == len(rows)
        assert 28 == len(handler.csv.header)

    def test_sample_prep__3_samples_are_created(self):
        # Arrange
        parser = CsvParser(
            handler_type='prep', project_code='YY-1111', path=prep_sample_submission_path_csv())
        ReplaceWith.contents_bag = ContentsBag(
            handler_type=parser.handler_type, project_code=parser.project_code, sample_list=parser.csv)

        handler = SampleSubmissionPrep(organization=self.handler_context.organization)

        # Act
        handler.handle(ReplaceWith.contents_bag.sample_list)

        # Assert
        expected = [
            'YY-1111-sample1',
            'YY-1111-sample2',
            'YY-1111-sample3',
        ]
        all_samples = Substance.objects.all()
        sample_names = [s.name for s in all_samples]
        assert set(expected).issubset(set(sample_names))

    def test_sample_prep__3_concentration_values_ok_fetched_from_substance_type(self):
        # Arrange
        ReplaceWith.contents_bag = CsvParser('prep', 'YY-1111', prep_sample_submission_path_csv())
        handler = SampleSubmissionPrep(organization=self.handler_context.organization)

        # Act
        handler.handle(ReplaceWith.contents_bag.csv)

        # Assert
        expected = {
            'YY-1111-sample1': 101,
            'YY-1111-sample2': 10,
            'YY-1111-sample3': 10,
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
        ReplaceWith.contents_bag = CsvParser('prep', 'YY-1111', prep_sample_submission_path_csv())
        handler = SampleSubmissionPrep(organization=self.handler_context.organization)

        # Act
        handler.handle(ReplaceWith.contents_bag.csv)

        # Assert
        expected = {
            'YY-1111-sample1': 101,
            'YY-1111-sample2': 10,
            'YY-1111-sample3': 10,
        }
        all_samples = ioc.app.substances.filter()
        conc_dict = dict()
        for sample in all_samples:
            conc_dict[sample.name] = sample.concentration

        assert expected == conc_dict

    def test_sample_prep__with_use_of_load_file__3_concentration_values_ok(self):
        # Arrange
        parser = CsvParser(
            handler_type='prep', project_code='YY-1111', path=prep_sample_submission_path_csv())
        ReplaceWith.contents_bag = ContentsBag(
            handler_type=parser.handler_type, project_code=parser.project_code, sample_list=parser.csv)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fake_file_obj)

        # Assert
        expected = {
            'YY-1111-sample1': 101,
            'YY-1111-sample2': 10,
            'YY-1111-sample3': 10,
        }
        all_samples = ioc.app.substances.filter()
        conc_dict = dict()
        for sample in all_samples:
            conc_dict[sample.name] = sample.concentration

        assert expected == conc_dict

    def test_sample_prep__all_udf_good(self):
        # Arrange
        parser = CsvParser(
            handler_type='prep', project_code='YY-1111', path=prep_sample_submission_path_csv())
        ReplaceWith.contents_bag = ContentsBag(
            handler_type=parser.handler_type, project_code=parser.project_code, sample_list=parser.csv)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fake_file_obj)

        # Assert
        samples = ioc.app.substances
        fetched_sample1 = samples.get(name='YY-1111-sample1')
        fetched_sample2 = samples.get(name='YY-1111-sample2')
        fetched_sample3 = samples.get(name='YY-1111-sample3')

        assert fetched_sample2.number_of_lanes == '1 lane/pool'
        assert fetched_sample3.number_of_lanes == '1 lane/pool'

        assert fetched_sample1.name == 'YY-1111-sample1'
        assert fetched_sample1.external_name == 'sample1'
        assert fetched_sample1.concentration == 101
        assert fetched_sample1.volume == 30
        assert fetched_sample1.sample_type == 'gDNA'
        assert fetched_sample1.coverage == '60x'
        assert fetched_sample1.volume_current == 30
        assert fetched_sample1.sample_delivery_date == '190829'
        assert fetched_sample1.container == 'YY-1111_PL1_org_190829'
        assert fetched_sample1.application == 'WG re-seq'
        assert fetched_sample1.species == 'Bos taurus'
        assert fetched_sample1.library_preparation_kit == 'TruSeq DNA PCR-Free Sample Preparation kit LT'
        assert fetched_sample1.libraries_per_sample == 1
        assert fetched_sample1.insert_size == '350'
        assert fetched_sample1.pooling == '10 libraries/pool'
        assert fetched_sample1.number_of_lanes == '2 flowcells/pool'
        assert fetched_sample1.special_info_library_prep is False
        assert fetched_sample1.seq_instrument == 'NovaSeq S4'
        assert fetched_sample1.read_length == '151x2'
        assert fetched_sample1.conc_flowcell_pm == '300 pM'
        assert fetched_sample1.phix_percent == 1
        assert fetched_sample1.custom_seq_primer is False
        assert fetched_sample1.special_info_sequencing is False
        assert fetched_sample1.genotyping_id_panel is False
        assert fetched_sample1.data_analysis == 'No'

    def test_ready_made_libraries__all_udf_good(self):
        # Arrange
        parser = CsvParser(
            handler_type='rml', project_code='XX-1111', path=rml_sample_submission_path_csv())
        ReplaceWith.contents_bag = ContentsBag(
            handler_type=parser.handler_type, project_code=parser.project_code, sample_list=parser.csv)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fake_file_obj)

        # Assert
        fetched_rml2 = ioc.app.substances.get_by_name('XX-1111-rml2')
        assert fetched_rml2.external_name == 'rml2'
        assert fetched_rml2.concentration == 2
        assert fetched_rml2.volume == 30
        assert fetched_rml2.sample_type == 'Ready-made library'
        assert fetched_rml2.application == 'Ready-made library'
        assert fetched_rml2.index_category is None
        assert fetched_rml2.index_number == '64-160'
        assert fetched_rml2.custom_index == 'GTCCGGC-AACCGAT'
        assert fetched_rml2.sample_index == 'Custom (GTCCGGC-AACCGAT)'

        assert fetched_rml2.volume_current == 30
        assert fetched_rml2.sample_delivery_date == '190529'
        assert fetched_rml2.container == 'XX-1111_PL1_org_190529'
        assert fetched_rml2.species == 'Vulpes lagopus'
        assert fetched_rml2.seq_instrument == 'HiSeqX'
        assert fetched_rml2.read_length == '151x2'
        assert fetched_rml2.number_of_lanes == '2 lanes/pool'
        assert fetched_rml2.conc_flowcell_pm == 'To be decided after QC'
        assert fetched_rml2.phix_percent == 1
        assert fetched_rml2.custom_seq_primer is False
        assert fetched_rml2.special_info_sequencing is False
        assert fetched_rml2.rml_kit_protocol == 'Meyer&Kircher 2010'

    def test_prep_submission__with_three_samples_on_same_plate__one_plate_created(self):
        # Arrange
        parser = CsvParser(
            handler_type='prep', project_code='YY-1111', path=prep_sample_submission_path_csv())
        ReplaceWith.contents_bag = ContentsBag(
            handler_type=parser.handler_type, project_code=parser.project_code, sample_list=parser.csv)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fake_file_obj)

        # Assert
        containers = ContainerRepository(self.organization)
        fetched_plate = containers.get(name='YY-1111_PL1_org_190829')

        assert fetched_plate is not None
        assert fetched_plate.name == 'YY-1111_PL1_org_190829'

    @pytest.mark.skip('waiting for new implementation of container')
    def test_prep_submission__with_3_samples_on_plate__sample_navigation_to_plate_is_ok(self):
        # Arrange
        contents = read_binary_file(prep_sample_submission_path())
        fileobj = BytesIO(contents)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fileobj)

        # Assert
        fetched_sample1 = ioc.app.substances.get_by_name('sample1')
        from clims.models.location import Location
        from clims.models.container import Container
        assert isinstance(fetched_sample1.location, Location)
        assert isinstance(fetched_sample1.location.container, Container)
        assert isinstance(fetched_sample1.container, Plate96)

    @pytest.mark.skip('Waiting for new implementation of container')
    def test_prep_submission__with_3_samples_on_plate__plate_navigation_to_sample_ok(self):
        # Arrange
        contents = read_binary_file(prep_sample_submission_path())
        fileobj = BytesIO(contents)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fileobj)

        # Assert
        containers = ContainerRepository(self.organization)
        plate1 = containers.get(name='YY-1111_PL1_org_190829')
        assert plate1 is not None
        assert plate1['A:1'].name == 'sample1'

    @pytest.mark.now
    def test_rml_submission__with_three_samples_on_same_plate__one_plate_created(self):
        # Arrange
        parser = CsvParser(
            handler_type='rml', project_code='XX-1111', path=rml_sample_submission_path_csv())
        ReplaceWith.contents_bag = ContentsBag(
            handler_type=parser.handler_type, project_code=parser.project_code, sample_list=parser.csv)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fake_file_obj)

        # Assert
        containers = ContainerRepository(self.organization)
        fetched_plate = containers.get(name='XX-1111_PL1_org_190529')

        assert fetched_plate is not None

    @pytest.mark.now
    def test_rml_submission__with_three_samples__one_pool_created(self):
        # Arrange
        parser = CsvParser(
            handler_type='rml', project_code='XX-1111', path=rml_sample_submission_path_csv())
        ReplaceWith.contents_bag = ContentsBag(
            handler_type=parser.handler_type, project_code=parser.project_code, sample_list=parser.csv)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", fake_file_obj)

        # Assert
        pool = ioc.app.substances.get_by_name('XX-1111-Pool1')
        assert pool is not None
        assert pool.volume == 30
        assert pool.concentration == 0.63
        assert len(pool.parents) == 4


class FakeFileObj():
    def read(self, dummy):
        pass


class CsvParser(object):
    def __init__(self, handler_type, project_code, path):
        self.handler_type = handler_type
        self.project_code = project_code
        self.path = path
        self.csv = Csv(self.path, delim='\t')


class ReplaceWith(object):
    contents_bag = None


fake_file_obj = FakeFileObj()


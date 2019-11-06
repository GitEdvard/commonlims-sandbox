from __future__ import absolute_import
import pytest
import logging
import os
from six import BytesIO
from sentry.testutils import TestCase
from sentry.models.file import File
from clims.handlers import SubstancesSubmissionHandler
from clims.handlers import HandlerContext
from clims.models.file import OrganizationFile
from clims.services.application import ioc
from sentry_plugins.snpseq.plugin.models import PrepSample
from sentry_plugins.snpseq.plugin.models import RmlSample
from sentry_plugins.snpseq.plugin.models import Pool
from sentry_plugins.snpseq.plugin.models import Plate96
from sentry_plugins.snpseq.plugin.handlers.sample_submission import SampleSubmissionHandler
from sentry.plugins import plugins
from commonlims.test.resources.resource_bag import prep_sample_submission_path
from commonlims.test.resources.resource_bag import read_binary_file


class TestSampleSubmissionOther(TestCase):
    def setUp(self):
        self.register_extensible(PrepSample)
        self.register_extensible(RmlSample)
        self.register_extensible(Pool)
        self.register_extensible(Plate96)
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        logger = logging.getLogger('clims.files')
        logger.setLevel(logging.CRITICAL)

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

    @pytest.mark.now
    def test_parse_prep_from_excel__internal_temp_file_is_deleted(self):
        # Arrange
        handler_context = HandlerContext(self.organization)
        handler = SampleSubmissionHandler(handler_context, self.app)
        org_file = self._create_organization_file(prep_sample_submission_path())

        # Act
        handler.handle(org_file)

        # Assert
        assert os.path.exists(handler.temp_file_name) is False

    def test_sample_prep__all_sample_udf_good(self):
        # Arrange
        contents = read_binary_file(prep_sample_submission_path())
        file_obj = BytesIO(contents)

        # Act
        plugins.load_handler_implementation(SubstancesSubmissionHandler, SampleSubmissionHandler)
        self.app.substances.load_file(self.organization, "the_file.xlsx", file_obj)

        # Assert
        fetched_sample1 = ioc.app.substances.get_by_name('YY-1111-sample1')

        assert fetched_sample1.concentration == 101
        assert fetched_sample1.external_name == 'sample1'
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
        assert fetched_sample1.special_info_library_prep is False
        assert fetched_sample1.number_of_lanes == '2 flowcells/pool'
        assert fetched_sample1.seq_instrument == 'NovaSeq S4'
        assert fetched_sample1.read_length == '151x2'
        assert fetched_sample1.conc_flowcell_pm == '300 pM'
        assert fetched_sample1.phix_percent == 1
        assert fetched_sample1.custom_seq_primer is False
        assert fetched_sample1.special_info_sequencing is False
        assert fetched_sample1.genotyping_id_panel is False
        assert fetched_sample1.data_analysis == 'No'

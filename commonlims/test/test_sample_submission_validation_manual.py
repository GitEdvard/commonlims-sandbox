from __future__ import absolute_import
import pytest
from sentry.testutils import TestCase
from clims.handlers import HandlerContext
from sentry_plugins.snpseq.plugin.handlers.sample_submission_validation import SampleSubmissionValidationHandler
from commonlims.test.resources.resource_bag import prep_sample_submission_failing_path
from commonlims.test.resources.resource_bag import new_excel_file_path


class TestSampleSubmissionValidationManual(TestCase):
    def setUp(self):
        self.context = HandlerContext(self.organization)

    @pytest.mark.now
    def test_prep_validation__manually_check_that_excel_is_formatted(self):
        # Arrange
        handler = SampleSubmissionValidationHandler(self.context, self.app)

        # Act
        handler.handle(prep_sample_submission_failing_path(), new_excel_file_path())

        # Assert
        self.assertEqual(1, 2, 'Check manually!')

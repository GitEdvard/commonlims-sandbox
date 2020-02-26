import unittest
from commonlims.utility.excel_rw import ExcelReadWriter
from commonlims.test.resources.resource_bag import prep_sample_submission_path
from commonlims.test.resources.resource_bag import new_excel_file_path


class TestExcel(unittest.TestCase):
    @unittest.skip('')
    def test_read_sample_submission_and_save_in_write_only_mode(self):
        excel_rw = ExcelReadWriter()
        excel_rw.load(prep_sample_submission_path())
        excel_rw.write_to_new_file(new_excel_file_path())

    def test_write_sample_submission_in_dual_mode__check_output_manually(self):
        excel_rw = ExcelReadWriter()
        excel_rw.load(
            prep_sample_submission_path(), data_only=False, read_only=False)
        excel_rw.write_with_dual_mode(new_excel_file_path())


from __future__ import absolute_import
import unittest
import pytest
from unittest import skip
from commonlims.test.resources.resource_bag import gemstone_csv_path
from commonlims.test.resources.resource_bag import read_gemstone_csv


class TestCsv(unittest.TestCase):
    def test_first(self):
        contents = read_gemstone_csv()
        print(contents)
        self.assertEqual(1, 1)

    def test_open_with_csv_class_and_input_filestream(self):
        from clims.services.file_service.csv import Csv
        with open(gemstone_csv_path(), 'r') as f:
            csv = Csv(f)
            for line in csv:
                print(line)

        self.assertEqual(1, 1)

    def test_open_with_csv_class_and_input_path(self):
        from clims.services.file_service.csv import Csv
        csv = Csv(gemstone_csv_path())
        for line in csv:
            print(line)

        self.assertEqual(1, 1)

    def test_write_specific_column_open_with_csv_class(self):
        from clims.services.file_service.csv import Csv
        csv = Csv(gemstone_csv_path())
        for line in csv:
            print(line['Color'])

        self.assertEqual(1, 1)

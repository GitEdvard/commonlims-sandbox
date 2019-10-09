import os
from StringIO import StringIO
from six import binary_type
from clims.handlers import SubstancesSubmissionHandler
from clims.services.file_service.csv import Csv
from commonlims.utility.gemstone_sample import GemstoneSample


class GemstoneSubmissionHandler(SubstancesSubmissionHandler):
    def handle(self, file_obj):
        csv = self._as_csv(file_obj)
        for line in csv:
            name = line['Sample ID']
            sample = GemstoneSample(name=name, organization=self.context.organization)
            sample.preciousness = line['Preciousness']
            sample.color = line['Color']
            sample.save()

    def _as_csv(self, file_obj):
        if file_obj.name.endswith('.csv'):
            csv = file_obj.as_csv()
        elif file_obj.name.endswith('.xlsx'):
            workbook = file_obj.as_excel()
            csv = self._xlsx_to_csv(workbook)
        else:
            _, ext = os.path.splitext(file_obj.name)
            NotImplementedError('File type not recognized: {}'.format(ext))
        return csv

    def _xlsx_to_csv(self, excel_workbook):
        sample_list_sheet = excel_workbook['Samples']
        rows = []
        for row in sample_list_sheet.iter_rows(min_row=3):
            line_contents = [binary_type(cell.value) for cell in row]
            line = ','.join(line_contents)
            rows.append(line)
        contents = '\n'.join(rows)
        file_like = StringIO(contents)
        return Csv(file_like)

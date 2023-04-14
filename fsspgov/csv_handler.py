import logging
from dataclasses import astuple
from typing import List

from win32com.client import Dispatch
from win32com.client.dynamic import CDispatch
from pathlib import Path

import constants as consts
import models
import exceptions


class CSVHandler:
    def __init__(self):
        self._file_input = consts.file_input
        self._file_output = consts.file_output
        self._csv_file = Dispatch('Excel.Application')

    def __del__(self):
        self._csv_file.Quit()

    # READ
    def read_excel(self) -> List[models.Debtors]:
        if not Path(Path.cwd() / self._file_input).is_file():
            raise FileNotFoundError

        file = self._csv_file.Workbooks.Open(Path.cwd() / self._file_input)
        sheet = file.ActiveSheet

        data_debtors = self._get_data_from_table(sheet, self._get_count_of_rows(sheet))
        self._check_input_data(data_debtors)

        file.Close()
        return data_debtors

    def _get_count_of_rows(self, sheet: CDispatch) -> int:
        result = 1

        while True:
            val_row = sheet.Cells(result, 1).value

            if str(val_row) != 'None':
                result += 1
            else:
                result -= 2
                break

        return result

    def _get_data_from_table(self, sheet: CDispatch, num_row: int) -> List[models.Debtors]:
        result = []

        data_row = []
        for i, val in enumerate(sheet.Range(f'A2:D{str(num_row + 1)}')):
            if (i+1) % 4 != 0:
                data_row.append(str(val))
            else:
                result.append(
                    models.Debtors(
                        data_row[0],
                        data_row[1],
                        data_row[2],
                        '.'.join(str(val).split(' ')[0].split('-')[::-1])
                    )
                )
                data_row.clear()

        return result

    def _check_input_data(self, input_data: List[models.Debtors]) -> None:
        if not input_data:
            logging.error('Исходных данных нет')
            raise exceptions.IncorrectInputDataException

    # WRITE
    def write_excel(self, data: List[models.Proceedings]):
        file = self._connecting_to_output_file()
        sheet = self._clearing_old_data(file)
        headers = consts.headers
        self._entering_title_text(sheet, headers)

        shift = 2
        for i, element in enumerate(data):
            if isinstance(element, List):
                sheet_range = sheet.Range(sheet.Cells(i+shift, 1), sheet.Cells(i+shift, 2))
                sheet_range.Value = element
            else:
                sheet_range = sheet.Range(sheet.Cells(i+shift, 1), sheet.Cells(i+shift, len(headers)))
                sheet_range.Value = astuple(element)

        file.Save()
        file.Close()

    def _connecting_to_output_file(self) -> CDispatch:
        if Path(Path.cwd() / self._file_output).is_file():
            file = self._csv_file.Workbooks.Open(Path.cwd() / self._file_output)
        else:
            file = self._csv_file.Workbooks.Add()
            file.SaveAs(str(Path.cwd()) + '/' + self._file_output)

        return file

    def _clearing_old_data(self, file: CDispatch) -> CDispatch:
        sheet = file.ActiveSheet
        sheet.UsedRange.Delete()

        return sheet

    def _entering_title_text(self, sheet: CDispatch, headers: List[str]) -> None:
        sheet.Range('A1:' + chr(64 + len(headers)) + '1').Value = headers

from dataclasses import dataclass
from typing import List


@dataclass
class Debtors:
    last_name: str
    first_name: str
    patronymic: str
    date: str


@dataclass
class Proceedings:
    debtor_data: str
    enforcement_proceedings_data: str
    details_of_executive_document_data: str
    date_reasonfor_end_or_termination_of_ie: str
    execution_subject_and_outstanding_debt_amount: str
    bailiff_department_data: str
    bailiff_executor_data: str


class ProceedingsHandler:
    def __init__(self, raw_form: List[str]):
        self._raw_form = raw_form

    @property
    def proceeding(self) -> Proceedings:
        return Proceedings(*self._raw_form)


# @dataclass
# class Proceedings:
#     # фамилия
#     last_name: str
#     # имя
#     first_name: str
#     # отчество
#     patronymic: str
#     # дата рождения
#     date: str
#     # место рождения
#     place_of_birth: str
#     # номер исполнительного производства
#     number_of_executive_prod: str
#     # дата возбуждения исполнительного производства
#     date_of_init_of_executive_prod: str
#     # вид исполнительного документа
#     executive_doc_type: str
#     # дата принятия органом исполнительного документа
#     date_adoption_executive_doc_by_agency: str
#     # номер исполнительного документа
#     number_executive_doc: str
#     # наименование органа, выдавшего исполнительный документ
#     agency_name_that_issued_executive_doc: str
#     # инн взыскателя-организации
#     inn_of_recoverer_organization: str
#     # дата и причина окончания или прекращения ип
#     date_reasonfor_end_or_termination_of_ie: str
#     # предмет исполнения
#     subject_of_execution: str
#     # сумма непогашенной задолженности
#     amount_of_outstanding_debt: str
#     # наименование отдела судебных приставов
#     name_of_bailiffs_department: str
#     # адрес отдела судебных приставов
#     address_of_bailiffs_department: str
#     # судебный пристав-исполнитель
#     bailiff_executor: str
#     # телефон для получения информации
#     phone_number_for_information: str
#
#
# class ProceedingsHandler:
#     def __init__(self, raw_form: List[str]):
#         self._raw_form = raw_form
#
#     @property
#     def proceeding(self) -> Proceedings:
#         return Proceedings(
#             *self._get_debtor_data(),
#             *self._get_enforcement_proceedings_data(),
#             *self._get_details_of_executive_document_data(),
#             *self._get_date_reasonfor_end_or_termination_of_ie(),
#             *self._get_execution_subject_and_outstanding_debt_amount(),
#             *self._get_bailiff_department_data(),
#             *self._get_bailiff_executor_data(),
#         )
#
#     def _get_debtor_data(self) -> List[str]:
#         raw_debtor_data = self._raw_form[0].split('\n')
#
#         return [
#             *raw_debtor_data[0].split(' '),
#             raw_debtor_data[1],
#             raw_debtor_data[2]
#         ]
#
#     def _get_enforcement_proceedings_data(self) -> List[str]:
#         return self._raw_form[1].split(' ', 1)
#
#     def _get_details_of_executive_document_data(self) -> List[str]:
#         raw_details = self._raw_form[2].split('\n')
#         part_of_raw_details = raw_details[0].split(' ')
#
#         return [
#             ' '.join(part_of_raw_details[:-2]),
#             ' '.join(part_of_raw_details[-4:-2]),
#             ' '.join(part_of_raw_details[-2:]),
#             raw_details[-2],
#             raw_details[-1],
#         ]
#
#     def _get_date_reasonfor_end_or_termination_of_ie(self) -> List[str]:
#         return [self._raw_form[3]]
#
#     def _get_execution_subject_and_outstanding_debt_amount(self) -> List[str]:
#         return self._raw_form[4].split('\n')
#
#     def _get_bailiff_department_data(self) -> List[str]:
#         return self._raw_form[5].split('\n')
#
#     def _get_bailiff_executor_data(self) -> List[str]:
#         return self._raw_form[6].split('\n')

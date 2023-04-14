import logging
import time
from typing import List

from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
    InvalidElementStateException
)

import constants as consts
import exceptions
import models


class FsspData:
    url = 'http://fssprus.ru/'

    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={UserAgent().chrome}')
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

        self._wait = WebDriverWait(self._driver, consts.wait)
        self._driver.implicitly_wait(consts.wait)

        self._restart()

    def __del__(self):
        self._driver.close()
        self._driver.quit()

    def _restart(self):
        self._driver.get(self.url)

        try:
            pop_up_window_button = self._wait.until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'button.tingle-modal__close'))
            )
            pop_up_window_button.click()

            self._installing_advanced_search_for_individual()

        except TimeoutException:
            self._restart()

    def _installing_advanced_search_for_individual(self):
        self._wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '.btn-light')))
        self._driver.find_element(By.CSS_SELECTOR, 'div.main-form__btn:nth-child(2) > button:nth-child(1)').click()
        self._wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'div.s-3:nth-child(1) > label:nth-child(1)')))
        self._driver.find_element(By.CSS_SELECTOR, 'div.s-3:nth-child(1) > label:nth-child(1)').click()

    def start(self, input_data: models.Debtors) -> List[models.Proceedings]:
        return self._get_data_from_source(input_data)

    def _get_data_from_source(self, input_data: models.Debtors) -> List[models.Proceedings]:
        all_data = []

        try:
            self._set_params(input_data)
            self._bypass_captcha()

            all_data = self._extract_data(input_data)
        except NoSuchElementException as ex:
            logging.error(f'Ни у одного элемента нет соответствующего атрибута имени класса:\n{ex}')
        except (TimeoutException, InvalidElementStateException, exceptions.RestartException) as ex:
            logging.warning(f'Перезапуск итерации сбора данных: {ex}')
            self._restart()
            all_data = self._get_data_from_source(input_data)
        except Exception as ex:
            logging.error(f'FsspData._get_data_from_source:\n{ex}')

        return all_data

    def _set_params(self, input_data: models.Debtors) -> None:
        for key in input_data.__dict__.keys():
            time.sleep(0.1)
            input_form = self._driver.find_element(By.NAME, f"is[{key}]")
            input_form.clear()
            input_form.send_keys(input_data.__getattribute__(key))
        self._driver.find_element(By.ID, 'btn-sbm').click()

    def _bypass_captcha(self) -> None:
        try:
            self._driver.find_element(By.CSS_SELECTOR, '.popup')
        except NoSuchElementException:
            return

        for i in range(consts.attempts):
            try:
                text = input()

                self._entering_captcha_text(text)
            except StaleElementReferenceException:
                continue
            except (TimeoutException, ElementNotInteractableException, NoSuchElementException):
                break

    def _entering_captcha_text(self, text: str) -> None:
        self._wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '#captcha-popup-code')))
        self._driver.find_element(By.ID, 'captcha-popup-code').send_keys(text)

        self._wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '#ncapcha-submit')))
        self._driver.find_element(By.CSS_SELECTOR, '#ncapcha-submit').click()

        self._wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '#ncapcha-submit')))

    def _extract_data(self, input_data: models.Debtors) -> List[models.Proceedings]:
        result = []
        self._check_result()
        num_pages = len(self._get_pagination()) - 1

        additional_pages = True
        while additional_pages:
            self._bypass_captcha()
            try:
                table = self._get_table()\
                    .find_element(By.CSS_SELECTOR, 'div.results-frame')\
                    .find_element(By.CSS_SELECTOR, 'tbody')
            except NoSuchElementException:
                result.append([
                    ' '.join([
                        input_data.last_name, input_data.first_name,
                        input_data.patronymic, input_data.date
                    ]),
                    'Задолженностей нет'
                ])
                break

            debts = self._get_data_from_table(table)
            result.extend(self._group_data_by_proceedings(debts))

            if num_pages > 0:
                pages = self._get_pagination()
                pages[len(pages) - 1].click()
                num_pages -= 1
            else:
                additional_pages = False

        return result

    def _check_result(self) -> None:
        self._get_table()

    def _get_table(self) -> WebElement:
        try:
            return self._driver.find_element(By.CSS_SELECTOR, 'div.results')
        except NoSuchElementException:
            raise exceptions.RestartException

    def _get_pagination(self) -> list:
        try:
            block_pages = self._driver.find_element(By.CSS_SELECTOR, 'div.pagination')
            result = block_pages.find_elements(By.TAG_NAME, 'a')
            return result
        except NoSuchElementException:
            return []

    def _get_data_from_table(self, table: WebElement) -> List[str]:
        debts = self._get_data_from_element(table, 'td')
        regions = self._get_data_from_element(table, 'h3')

        for reg in regions:
            debts.remove(reg)
        del debts[4::8]

        return debts

    def _get_data_from_element(self, table: WebElement, element: str) -> List[str]:
        return list(map(self._get_text, table.find_elements(By.TAG_NAME, element)))

    def _get_text(self, element) -> str:
        return element.text

    def _group_data_by_proceedings(self, debts: List[str]) -> List[models.Proceedings]:
        proceedings = []

        for i in range(len(debts)//7):
            try:
                raw_form = self._get_raw_form_of_proc_data(debts, i)
                proceeding = models.ProceedingsHandler(raw_form).proceeding
                proceedings.append(proceeding)
            except StaleElementReferenceException:
                continue

        return proceedings

    def _get_raw_form_of_proc_data(self, debts: List[str], i: int) -> List[str]:
        return [x.replace('\n', ', ') for x in debts[i*7:i*7+7]]

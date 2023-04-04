import time
from typing import List, Dict

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager

import constants as consts
import models


class MosGorSudData:
    url = 'https://mos-gorsud.ru/search'

    def __init__(self, params: Dict[str, str]) -> None:
        options = webdriver.ChromeOptions()
        useragent = UserAgent()
        options.add_argument(f'user-agent={useragent.chrome}')
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

        self._params = params

    def start(self) -> List[models.CourtCase]:
        return self._get_data_from_source()

    def _get_data_from_source(self) -> List[models.CourtCase]:
        all_data = []

        try:
            self._driver.get(self.url)

            self._set_params()

            all_data = self._extract_data()
        except NoSuchElementException as ex:
            # TODO залогировать
            print(f'No element has a matching class name attribute: {ex}')
        except Exception as ex:
            # TODO залогировать
            print(f'Unexpected error!\n{ex}')
        finally:
            self._driver.close()
            self._driver.quit()

        return all_data

    def _set_params(self) -> None:
        elements = self._get_params(
            self._params['court'],
            self._params['instance'],
            self._params['process'],
        )
        elements.append(consts.button)

        for element in elements:
            time.sleep(0.01)

            element = self._driver.find_element(By.ID, element)
            webdriver.ActionChains(self._driver).move_to_element(element).click(element).perform()

    def _get_params(self, court: str, instance: str, process: str):
        return [
            consts.params['суд']['класс'],
            consts.params['суд']['список'][court],
            consts.params['инстанция']['класс'],
            consts.params['инстанция']['список'][instance],
            consts.params['производство']['класс'],
            consts.params['производство']['список'][process],
        ]

    def _extract_data(self) -> List[models.CourtCase]:
        all_data = []

        page_num = 1
        max_pages = int(
            self._driver.find_element(By.ID, 'paginationFormMaxPages').get_attribute("value")
        )
        while page_num <= max_pages:
            self._go_to_specific_page(page_num)

            rows = self._extract_data_from_page()
            all_data.extend(rows)

            page_num += 1
            time.sleep(0.01)

        return all_data

    def _go_to_specific_page(self, page_num: int) -> None:
        pagination_form_input = self._driver.find_element(By.ID, 'paginationFormInput')
        pagination_form_input.send_keys(Keys.CONTROL + 'a' + Keys.DELETE)
        pagination_form_input.send_keys(f'{page_num}\n')

    def _extract_data_from_page(self) -> List[models.CourtCase]:
        table = self._driver.find_element(By.CLASS_NAME, 'custom_table')
        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]

        result = []
        for row in rows:
            record_cells = row.find_elements(By.TAG_NAME, 'td')

            #  категория дела
            if record_cells[5].text != consts.case_category:
                continue

            result.append(
                models.CourtCase(
                    record_cells[0].text,
                    record_cells[1].text,
                    record_cells[2].text,
                    record_cells[3].text,
                    record_cells[4].text,
                    record_cells[5].text,
                    record_cells[6].find_element(By.TAG_NAME, 'a').get_attribute("textContent"),
                )
            )

        return result

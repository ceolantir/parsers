from datetime import datetime, timedelta
from typing import List, Tuple, Dict

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager

import exceptions
import models


class RateStatsData:
    url = 'https://ratestats.com/day/'

    def __init__(self, delta: int) -> None:
        options = webdriver.ChromeOptions()
        useragent = UserAgent()
        options.add_argument(f'user-agent={useragent.random}')
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
        )

        self._delta = delta

    def start(self) -> Dict[str, List[models.Currency]]:
        return self._get_data_from_source()

    def _get_data_from_source(self) -> Dict[str, List[models.Currency]]:
        # TODO сделать датакласс
        all_data = []
        try:
            all_data = self._extract_data()
        except NoSuchElementException as ex:
            # TODO залогировать
            print(f'No element has a matching class name attribute: {ex}')
        except exceptions.DateDeltaError as ex:
            # TODO залогировать
            print(ex)
        except Exception as ex:
            # TODO залогировать
            print(f'Unexpected error!\n{ex}')
        finally:
            self._driver.close()
            self._driver.quit()

        return all_data

    def _extract_data(self) -> Dict[str, List[models.Currency]]:
        all_data = {}

        for url, date in map(self._get_url_for_specific_day, self._get_delta_days()):
            self._driver.get(url=url)
            raw_data = self._driver.find_element(By.XPATH, '//tbody').text

            all_data[date] = self._transfer_to_normal_form(raw_data)

        return all_data

    def _get_url_for_specific_day(self, date: str) -> Tuple[str, str]:
        return f'{self.url}{date}/', f'{date[:4]}-{date[4:6]}-{date[6:]}'

    def _get_delta_days(self) -> List[str]:
        result = []
        d2 = datetime.today()
        d1 = datetime.today() - timedelta(days=self._delta)

        date_delta = d2 - d1
        if date_delta.days <= 0:
            raise exceptions.DateDeltaError
        for i in range(date_delta.days + 1):
            result.append((d1 + timedelta(i)).strftime('%Y%m%d'))

        return result

    def _transfer_to_normal_form(self, raw_data: str) -> List[models.Currency]:
        result = []

        for raw_row in raw_data.split('\n'):
            row = raw_row.split()
            result.append(
                models.Currency(
                    row[0], ' '.join(row[1:-4]), row[-4],
                    f'{row[-3]} {row[-2]}', row[-1],
                )
            )

        return result

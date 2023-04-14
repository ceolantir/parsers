import logging

import extractions
import csv_handler

logging.basicConfig(level=logging.WARNING, filename="logs/log.log", filemode="w")

if __name__ == "__main__":
    csv = csv_handler.CSVHandler()
    input_data = csv.read_excel()

    session = extractions.FsspData()
    result = []
    for row in input_data:
        result.extend(session.start(row))

    csv.write_excel(result)

import csv
import json
from io import TextIOWrapper
from json import JSONDecodeError
from logging import exception

from matplotlib.cbook import flatten

from detector.models import Transaction


def process_csv(input_file):
    data = TextIOWrapper(input_file, encoding='utf-8')
    reader = csv.DictReader(data)
    data_to_insert = []

    # Skip first row containing headers
    # next(reader, None)

    # Stop pycharm from complaining with type hinting
    row: dict
    for row in reader:
        velocity = flatten_velocity(row, 'velocity_last_hour')
        row.update(velocity)
        try:
            data_to_insert.append(Transaction(**row))
        except Exception as e:
            print(f"Error processing row {row}: {e}")

    Transaction.objects.bulk_create(data_to_insert)

def flatten_velocity(row, fieldname):
    json_string = row[fieldname]
    row.pop(fieldname)

    json_string = json_string.replace("'", '"')
    try:
      parsed = json.loads(json_string)
      # append v_ to the beginning of original values
      return {f"v_{key}": value for key, value in parsed.items()}
    except JSONDecodeError as e:
        print(f'Error decoding {fieldname}, {e}')


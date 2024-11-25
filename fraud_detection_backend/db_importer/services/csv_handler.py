import csv
import json
from io import TextIOWrapper


def process_csv(input_file):
    data = TextIOWrapper(input_file, encoding='utf-8')
    reader = csv.reader(data)
    for row in reader:
        print(row)

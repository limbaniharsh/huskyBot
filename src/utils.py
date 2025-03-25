import csv
import os
import json

def read_file_url_mapper(filename):
    """
    Reads the contents of a CSV file and returns the data as a list of dictionaries.

    Each dictionary corresponds to a row in the CSV file, with the keys 
    being the column names ("file", "URL").

    If the file doesn't exist, it returns an empty list.
    """
    if not os.path.exists(filename):
        return []  # Return an empty list if the file doesn't exist

    with open(filename, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def write_dict_as_json(file_path, dictionary):
    with open(file_path, "w") as f:
        json.dump(dictionary, f, indent=4)
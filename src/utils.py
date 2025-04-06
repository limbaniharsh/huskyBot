import csv
import os
import json
import logging

from IPython.testing.tools import default_config

import config


app_config = config.Config.default_config()

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


def setup_logger(name: str, log_file_path):
    """Setup a logger with a specific name to log only to a file."""
    if name is None:
        name  = app_config.app_name
    if log_file_path is None:
        log_file_path = app_config.log_file
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
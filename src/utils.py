import csv
import os
import json
import logging
from config import Config



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


def setup_logger(config=None):
    """Setup a logger with a specific name to log only to a file."""
    if config is None:
        config = Config.default_config()

    name  = config.app_name
    log_file_path = config.log_file
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

def get_logger():
    config = Config.default_config()
    return logging.getLogger(config.app_name)
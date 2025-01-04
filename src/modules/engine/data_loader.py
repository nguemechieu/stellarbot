import io
import logging
import os

import pandas as pd


def process_data(data):
    read_data = pd.read_csv(io.StringIO(data))
    return read_data


class DataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir or '.'  # Default to current directory if no data_dir provided
        self.data_files = os.listdir(data_dir)
        self.data = {}
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def get_data(self, filename):
        if filename in self.data:
            return self.data[filename]
        else:
            data = self.load_data(filename)
            if data is not None:
                self.data[filename] = data
                self.logger.info(f"Loaded data for {filename}")
                return data
            else:
                return None

    def load_data(self, filename):
        filepath = os.path.join(self.data_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                data = file.read()
                self.logger.info(f"Loaded data for {filename}")
                return process_data(data)
        else:
            self.logger.warning(f"Data file {filename} not found")
            #Create a new file if it doesn't exist
            with open(filepath, 'w') as file:
                file.write('')
            return None

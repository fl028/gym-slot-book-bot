import logging
import os
import json

class Logger:
    def __init__(self, level=logging.INFO):
        self.root_directory = os.path.dirname(os.path.abspath(__file__)).split("src")[0]

        # constants
        file_path_constants = os.path.join( self.root_directory , 'src','data','constants.json')
        with open(file_path_constants, 'r', encoding='utf-8') as file:
            json_data_constants = file.read()
        self.constants_data_dict = json.loads(json_data_constants)

        self.logger = logging.getLogger(self.constants_data_dict["logger"])
        self.logger.setLevel(level)

        file_handler = logging.FileHandler(self.constants_data_dict["logfile"])
        file_handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)
        print(message)

    def warning(self, message):
        self.logger.warning(message)
        print(message)

    def error(self, message):
        self.logger.error(message)
        print(message)

    def debug(self, message):
        print(message)
import abc
import os

class DataLoader(metaclass=abc.ABCMeta):
    _container = None

    @abc.abstractmethod
    def __init__(self, file_name: str):
        return NotImplemented
    
    @abc.abstractmethod
    def extract_data(self, variable_name: str):
        return NotImplemented
    
    def check_file_exist(self, file_name: str):
        assert os.path.exists(file_name), f'{file_name} does not exist!'

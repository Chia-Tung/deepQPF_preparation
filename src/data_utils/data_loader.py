import abc

class DataLoader(metaclass=abc.ABCMeta):
    _container = None

    @abc.abstractmethod
    def __init__(self, file_name: str):
        return NotImplemented
    
    @abc.abstractmethod
    def extract_data(self, variable_name: str):
        return NotImplemented

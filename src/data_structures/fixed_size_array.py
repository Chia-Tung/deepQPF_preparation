import numpy as np
import json

class FixedSizeArray:
    def __init__(self, pre_data:str = None) -> None:
        self._length = 6
        self._shape = (561, 441)
        self._invalid_value = 0
        self._factor = 6
        self._cnt = 0

        self._data = np.full(
            [self._length, self._shape[0], self._shape[1]], 
            self._invalid_value,
            dtype=np.float32
        )
        self._pre_data = pre_data
        if pre_data != None: 
            self.load_predata()
        
    def load_predata(self, json_path = ""):
        if json_path:
            # model prediction use
            with open(json_path, "r") as f:
                data_dict = json.load(f)

            for i in range(self._length-5):
                old_fix_array = data_dict[str(i)]
                if len(old_fix_array) == 0:
                    continue
                for triplet in old_fix_array:
                    self._data[i][triplet[0], triplet[1]] = triplet[2] / self._factor
            print(self._data.max())

        else:
            with open(self._pre_data, "r") as f:
                data_dict = json.load(f)
        
            for i in range(1, self._length):
                old_fix_array = data_dict[str(i)]
                if len(old_fix_array) == 0:
                    continue
                for triplet in old_fix_array:
                    self._data[i-1][triplet[0], triplet[1]] = triplet[2] / self._factor

    @property
    def data(self):
        return self._data * self._factor
    
    @property
    def cnt(self):
        return self._cnt

    def fit_mask(self, mask):
        for i in range(self._length):
            self._data[i][mask == 1] = 0
    
    def five_sum(self):
        return np.sum(self._data[1:], axis=0)

    def append(self, new_data):
        assert new_data.shape == self._shape, f"Wrong shape of new appended data!"

        # update counter
        self._cnt += 1
        
        # pop and add
        self._data = np.delete(self._data, 0, axis=0)
        self._data = np.concatenate([self._data, new_data[None]], axis=0)
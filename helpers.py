import json

class StaticVariables:
    def __init__(self) -> None:        
        with open('var.json', 'r') as f:
            self.data = json.load(f)

        # preprocess
        self.base_color = int(self.data['base_color'], 16)

    def __getitem__(self, __name: str) -> any:
        return self.data[__name]
    
    def __getattribute__(self, __name: str) -> any:
        if __name == 'data':
            return object.__getattribute__(self, 'data')
        return self.data[__name]

    def __setattr__(self, __name: str, __value: any) -> None:
        if __name != 'data':
            self.data[__name] = __value
        else:
            object.__setattr__(self, __name, __value)

        with open('var.json', 'w') as f:
            json.dump(self.data, f)
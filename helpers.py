import json
import csv


class Var:
    def __init__(self) -> None:
        with open('./data/var.json', 'r') as f:
            self.data = json.load(f)

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

        with open('./data/var.json', 'w') as f:
            json.dump(self.data, f, indent=4)


def check_in_csv(item, fp, i):
    with open(fp, "r") as f:
<<<<<<< HEAD
        reader = csv.reader(f)
        items = [str(row[0]) for row in reader]
        print(items)
=======
        reader = csv.reader(f, delimiter=",")
        
        if i == 0:
            return item.lower() in [str(row[0]).lower() for row in reader]
        elif i == 1:
            return item.lower() in [row[0].lower().split(";")[1].strip('"') for row in reader]
>>>>>>> fb972f1a5759b452ef2c1504efbeccd578d0b767

        
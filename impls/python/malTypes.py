from typing import Tuple, List

class MalType:
    pass

class Symbol(MalType):
    _symbol: str

    def __init__(self, token: str):
        self._symbol = token

    def __repr__(self):
        return self._symbol

    def __str__(self):
        return self.__repr__()

    def get_value(self):
        return self._symbol

class String(MalType):
    _val: str

    def __init__(self, token: str):
        self._val = token

    def __repr__(self):
        return self._val

    def __str__(self):
        return self.__repr__()

    def get_value(self):
        return self._val

    

class Num(MalType):
    _value: int|float

    def __init__(self, token: str):
        try: 
            if "." in token:
                self._value = float(token)
            else:
                self._value = int(token)
        except Exception as e:
            raise ValueError(f"Failure in Num init atempting to parse {token} into a numeric value") 

    def __repr__(self):
        return str(self._value)

    def __str__(self):
        return self.__repr__()

    def get_value(self):
        return self._value


class MalFalse(MalType):

    def __repr__(self):
        return "false"

    def __str__(self):
        return self.__repr__()

    def get_value(self):
        return False


class MalTrue(MalType):

    def __repr__(self):
        return "true"

    def __str__(self):
        return self.__repr__()

    def get_value(self):
        return True


class Nil(MalType):
    # Sorta unsure about this implementation, may need revision later

    def __repr__(self):
        return "nil"
    
    def __str__(self):
        return self.__repr__()

    def get_value(self):
        return None


class MalList(MalType):
    _mal_list: Tuple

    class MalIter:
        _list: Tuple
        _idx: int = 0

        def __init__(self, parent):
            self._list = parent.get_value()

        def __next__(self) -> MalType:
            if self._idx < len(self._list):
                item: MalType = self._list[self._idx] 
                self._idx += 1
                return item
            raise StopIteration()

    def __init__(self, members):
        try:
            for member in members:
                assert isinstance(member, MalType)
        except AssertionError as e:
            print([(m, type(m)) for m in members])
            raise e
        self._mal_list = tuple(members)  

    def __iter__(self):
        return self.MalIter(self)

    def __repr__(self):
        rep = "("
        for member in self._mal_list:
            rep += f" {str(member) }"
        rep += ")"
        return

    def __str__(self):
        return self.__repr__()

    def size(self) -> int:
        return len(self._mal_list)
    
    def get_value(self) -> Tuple[MalType]:
        return self._mal_list

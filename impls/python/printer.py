from malTypes import *


def pr_str(obj: MalType) -> str:
    if isinstance(obj, Symbol) or isinstance(obj, String):
        return obj.get_value()
    elif isinstance(obj, Num):
        return  str(obj.get_value())
    elif isinstance(obj, Nil):
        return "nil"
    elif isinstance(obj, MalTrue):
        return "true"
    elif isinstance(obj, MalFalse):
        return "false"
    elif isinstance(obj, MalList):
        return "(" + " ".join([pr_str(member) for member in obj]) + ")"
    else:
        t = type(obj)
        raise TypeError(f"pr_str cannot handle type: {t}")

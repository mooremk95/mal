import re
from typing import Tuple
from malTypes import MalType, MalList, Num, Symbol, MalFalse, MalTrue, Nil, String

"""
This module is a class and collection of funcitons which serve to read in a line of MAL code and generate an 
AST for later evaluation. 
"""

MAL_PATTERN = re.compile(r"[\s,]*(~@|[\[\]{}()'`~^@]|\"(?:\\.|[^\\\"])*\"?|;.*|[^\s\[\]{}('\"`,;)]*)")

class Reader:
    """
    This class works as a stateful reader for a parsed sequence of tokens over a line entered by the repl user. 
    """    
    _tokens: Tuple = None
    _index: int = 0

    def __init__(self, tokens):
        self._tokens = tokens
    
    def peak(self):
        if self._tokens is None:
            raise AttributeError(f"Reader {self} has no tokens list") 
        elif self._index >= len(self._tokens):
            raise EOFError(f"Index {self._index} is our of range [0 - {len(self._tokens)}]")
        return self._tokens[self._index]

    def next(self):
        if self._tokens is None:
            raise AttributeError(f"Reader {self} has no tokens list") 
        elif self._index >= len(self._tokens):
            raise EOFError(f"Index {self._index} is our of range [0 - {len(self._tokens)}]")
        token = self._tokens[self._index]
        self._index += 1
        return token

def read_from(reader: Reader) -> MalType:
    """ 
    Peaks at the next token and decides whether to call read_list (if it sees a "(")) or otherwise
    calls read_atom
    """
    token = reader.peak()
    # Tests seme to implt {} and [] make lists too
    #if token.startswith("(")
    if len(token) > 0 and token[0] in ("(", "[", "{"):
        # Kinda hacky, but discard the 1st token of a list so as not to cause infinite recursion
        # _ = reader.next() 
        return read_list(reader)
    else:
        return read_atom(reader)

def read_list(reader: Reader) -> MalList:
    """ 
    Iteratively uses the return from read_from to extend a MalList until the ")" token is encountered. 
    Then returns said completed MalList.
    """
    closers = {"(": ")", "[": "]", "{": "}"}
    raw_mal_list = []
    closer = closers[reader.next()]
    token: str = reader.peak()
    #Use a while loop and break only when we see a sym ending in ")"
    while not token.endswith(closer):
        raw_mal_list.append(read_from(reader))
        token = reader.peak()
    # once we see the closing ")" call next to remove it from the token sequence
    reader.next()
    return MalList(raw_mal_list)

def read_atom(reader: Reader):
    """ 
    Reads a token as an atom. An atom is any MAL type which is not a list.
    """
    token: str = reader.next().strip()
    if token == "nil":
        return Nil()
    elif token == "true":
        return MalTrue()
    elif token == "false":
        return MalFalse()
    elif token.startswith('"'): 
        if token.endswith('"'):
            return String(token)
        raise EOFError(f"Token: {token} is an unbalanced string")
    elif token.startswith("'"):
        if token.endswith("'"):
            return String(token)
        raise EOFError(f"Token: {token} is an unbalanced string")
    elif is_int(token) or is_float(token):
        return Num(token)
    else:
        return Symbol(token)

def is_float(token: str):
    return re.compile(r"[+-]?(\d*\.\d+)|(\d+.)").fullmatch(token) is not None

def is_int(token: str):
    return re.compile(r"[-+]?\d+").fullmatch(token) is not None

def read_str(ipt: str) -> MalType:
    """
    Simple function to tokenize an input striing, then pass to a reader to read from for 
    parsing.  
    """
    tokens: Tuple =  tokenize(ipt)
    reader: Reader = Reader(tokens)
    return read_from(reader)


def tokenize(statement: str) -> Tuple[str]:
    """
    Function which uses a regex to identify MAL tokens (keywords, key characters, numbers, strings, symbols). This simply generates a sequence of 
    tokens in the form of a tuple. This function does not concern itself with the MAL data types. 
    """
    # get group 1 rather than gorup 0 is the entire match, and may include useless whitespace characters
    return tuple(match.group(1) for match in MAL_PATTERN.finditer(statement))




if __name__ == "__main__":
    """ """
    list_exprs = [
        "(+ 5 1)",
        "(- 40 20)",
        " ( + 7 7 7 7    7) ",
        "( * 4 (+ 3 2))",
        "(testing (lists) (with multiple ) (lists (inside)))"
        "(test (commas,as,whitespace))"
        ""
    ]
    for expr in list_exprs:
        tokens = tokenize(expr)
        print(f"Tokens for {expr=}\n\t" + "\n\t".join(tokens))

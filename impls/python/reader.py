import re
from typing import Tuple, List
from malTypes import *

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
    if len(token) > 0 and token[0] in ("(", "[", "{"):
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
    # once we see the closing c call next to remove it from the token sequence
    reader.next()
    # Then decide what type of "list" this is 
    if "]" == closer:
        return Vector(raw_mal_list)
    elif "}" == closer:
        return HashMap(raw_mal_list)
    else: 
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
    elif token.startswith(":"):
        return Keyword(token)
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
    Function which uses a regex to identify MAL tokens (keywords, key cacters, numbers, strings, symbols). This simply generates a sequence of 
    tokens in the form of a tuple. This function does not concern itself with the MAL data types. 
    """
    statement = apply_macros(strip_comments(statement))
    if not verify_pairs_close(statement):
        raise EOFError("Expression entered is unbalanced in one of (), [], \{\} \"\" or \\")
    # get group 1 rather than gorup 0 is the entire match, and may include useless whitespace cacters
    return tuple(match.group(1) for match in MAL_PATTERN.finditer(statement))

def strip_comments(statement: str) -> str:
    if ";" == statement:
        return ""
    if ";" in statement:
        in_quotes = False
        for i, c in enumerate(statement):
            if '"' == c:
                in_quotes = not in_quotes
                continue
            if not in_quotes and ";" == c:
                return statement[:i]
    return statement

def apply_macros(statement: str) -> str:
    # apply quotes
    result = apply_macro(statement, "'", "quote") 
    # apply quasiquotes
    result = apply_macro(result, "`", "quasiquote") 
    # apply unquotes
    result = apply_macro(result, "~", "unquote")
    # apply splize-unquote
    result = apply_macro(result, "~@", "splice-unquote") 
    # apply deref
    result = re.sub(r"@([0-9A-z?!$\?-]+)", r"(deref \g<1>)", result)
    return result

def apply_macro(statement: str, macro_chars: str, substitution: str) -> str:
    """
    Arguably hacky, but iteratively apply regex substitution to handle nested quote macros.
    """
    last = statement
    new = re.sub(f"{macro_chars}([0-9A-z-?_]+|\([ 0-9A-z-?_'`~@]+\))", 
                    f"({substitution} \g<1>)",
                    statement)
    while new != last:
        last = new
        new = re.sub(f"{macro_chars}([0-9A-z-?_]+|\([ 0-9A-z-?_'`~@]+\))", 
                    f"({substitution} \g<1>)",
                    last)
    return new


def verify_pairs_close(in_str: str) -> bool:
    """ 
    This function takes the input string, matches ()'s []'s, {}'s and unescaped "s and 's
    If it doesn't find a corresponding closing c for each opening char it returns False, else True
    """
    closers: Tuple = (")", "]", "}")
    openers: tuple = ("(", "[", "{")
    closer_to_opener: Dict = {")": "(", "]": "[", "}": "{"}
    last_open: List[Str] = []  # list functions as a stack of seen openers
    in_quotes = False
    escapes = 0
    for c in in_str: 
        # check if we are adding a sequential escaping via the "\"
        if "\\" == c:
            escapes += 1
            continue
        # when we're in quotes, all we care about is exiting quotes
        if not escapes % 2 and '"'  == c:
            in_quotes = not in_quotes
        if in_quotes:  # skip when we find outselves in quotes w/ non "\" char 
            escapes = 0
            continue
        if c in openers:   
            last_open.append(c)
        elif c in closers:
            if closer_to_opener[c] == last_open[-1]:
                last_open.pop()
            else:
                return False
        # If we get here, we processed a non "\" char, meaning we reset escapes
        escapes = 0 
    return not escapes % 2 and len(last_open) == 0 and not in_quotes



if __name__ == "__main__":
    """ """
    list_exprs = [
        "(+ 5 1)",
        "(- 40 20)",
        " ( + 7 7 7 7    7) ",
        "( * 4 (+ 3 2))",
        "(testing (lists) (with multiple ) (lists (inside)))",
        "(test (commas,as,whitespace))",
        "'(1 2 3)",
        "`1",
        "~1",
        "~@(1 2 3)"

    ]
    for expr in list_exprs:
        tokens = tokenize(expr)
        print(f"Tokens for {expr=}\n\t" + "\n\t".join(tokens))

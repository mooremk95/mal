#TODO: Work on some deferrable functionality
# macro replacements (see test1)

"""
- 'a -> (quote a)
- '(a b c... n) -> (quote (a b c... n))
- `a -> (quasiquote a)
- `(a b c... n) -> (quasiquote a b c... n)
- ~a -> (unqote a)
- ~(1 2 3) -> (unquote (1 2 3))
- `(1 ~a 3) -> (quasiquote (1 (unquote a) 3))
- ~a(1 2 3) -> (splice-unquote (1 2 3))
"""
import sys, traceback

from malTypes import MalType
from reader import read_str
from printer import pr_str


PROMPT = "user> "

def READ(inp: str) -> MalType:
    return read_str(inp)

def EVAL(ast: str, env: dict|None):
    return ast

def PRINT(ast: MalType): 
    return pr_str(ast)

def rep(inp: str):
    return PRINT(EVAL(READ(inp), None))

def main():
    while True:
        try:
            line: str = input(PROMPT)
            if line is None:
                break
            elif "(exit)" == line.replace(" ", "").replace("\t", ""):
                break
            print(rep(line))
        except EOFError as e:
            print('EOF error. Expression was missing one or more closing brace or string quote') 
        except Exception as e:
            # For non EOF exceptions print a traceback for debugging
            print(" ".join(traceback.format_exception(e)))
            break

if __name__ == "__main__":
    main()

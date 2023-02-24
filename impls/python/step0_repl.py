# TODO: Implement history functionality here
import sys, traceback

PROMPT = "user> "
EOF = ""

def READ(inp: str):
    return inp

def EVAL(ast: str, env: dict|None):
    return ast

def PRINT(exp: str): 
    return exp

def rep(inp: str):
    return PRINT(EVAL(READ(inp), None))

def main():
    while True:
        try:
            line: str = input(PROMPT)
            if line is None:
                break
            print(rep(line))
        except EOFError as e:
            print()
            break
        except Exception as e:
            # For non EOF exceptions print a traceback for debugging
            print(" ".join(traceback.format_exception(e)))
            break

if __name__ == "__main__":
    main()

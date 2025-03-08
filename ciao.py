import graphviz
from copy import deepcopy
from build_ast import GetAST
from R_ast import GenerateCode
import sys


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ciao <filename>")
    else:
        ciao_programm_file = sys.argv[1]
        ciao_json_file = 'ciao.json'
        ast = GetAST(ciao_json_file, ciao_programm_file, True)
        print(GenerateCode(ast, "test.txt"))
        print(ast)


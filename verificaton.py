import graphviz
from copy import deepcopy
from build_ast import GetAST


if __name__ == "__main__":
    ciao_json_file = 'ciao.json'
    ciao_programm_file = 'Caio programs/TrafficLight.txt'
    ast = GetAST(ciao_json_file, ciao_programm_file, True)
    print(ast)

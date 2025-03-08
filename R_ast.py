from scanner import Tokenize
from afterscan import Afterscan
from dsl_token import *
from syntax import *
import graphviz
import json
import pathlib
import os


def __GetRCode(node):
    key = "$ATTRIBUTE$"

    # Обработка терминалов
    if TreeNode.Type.NONTERMINAL != node.type:
        # Возвращаем токен как элемент списка
        return [node.token.str]

    # Обработка нетерминалов
    result = []

    # Рекурсивная обработка дочерних узлов
    for i in range(len(node.childs)):
        child_code = __GetRCode(node.childs[i])
        result.extend(child_code)

    return result


def GenerateCode(ast, output_file=None):
    """
    Генерирует исполняемый код из AST
    Args:
        ast (TreeNode): Корень абстрактного синтаксического дерева
        output_file (str/None): Путь для сохранения результата (если требуется)
    Returns:
        str: Сгенерированный код или сообщение об ошибке
    """
    try:
        generated_code = __GetRCode(ast)
        code = format_text(generated_code)
        with open("out.txt", 'w') as f:
            f.write(code)
        return code

    except RuntimeError as e:
        error_msg = f"Code generation error: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return error_msg


def format_text(words):
    formatted_text = []
    indent_level = 0
    i = 0
    n = len(words)

    while i < n:
        word = words[i]

        # Первый уровень: начинается с "ciao"
        if word == "ciao":
            formatted_text.append(word + " " + words[i + 1])
            i += 2
            indent_level = 1

        # Второй уровень: начинается с "class" или "scheme"
        elif word == "class":
            indent_level = 1
            formatted_text.append("  " * indent_level + word + " " + words[i + 1])
            i += 2
            indent_level = 2

        elif word == "scheme":
            indent_level = 1
            formatted_text.append("  " * indent_level + word)
            i += 1
            indent_level = 2

        # Третий уровень: ключевые слова после "class"
        elif word in ["events", "effects", "conditions", "assertions", "variables", "states"]:
            indent_level = 2
            formatted_text.append("  " * indent_level + word)
            i += 1
            indent_level = 3

        # Третий уровень: ключевые слова после "scheme"
        elif word in ["objects", "links", "private", "public"]:
            indent_level = 2
            formatted_text.append("  " * indent_level + word)
            i += 1
            indent_level = 3

        # Четвертый уровень: обработка строк после ключевых слов
        else:
            line = "  " * indent_level + word
            i += 1
            list_key = ["->", "<-", "=", ":=", ":", ";", ",", ".", "new", "else", "(", ")", "[", "]", "/"]
            list_non_space = [".", ")", "[", "]"]
            while i < n and (words[i] in list_key or
                             words[i - 1] in list_key):
                line += ("" if words[i] in list_non_space or
                               words[i - 1] in (list_non_space + ["("]) else " ")\
                        + words[i]
                if words[i] == ")":
                    i += 1
                    break
                i += 1
            formatted_text.append(line)

    return "\n".join(formatted_text)


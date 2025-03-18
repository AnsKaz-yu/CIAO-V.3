from syntax import *
import dsl_info_ciao as dsl_info
from itertools import groupby
import pprint


def __GetNodeCode(node):
    # Обработка терминалов
    if TreeNode.Type.NONTERMINAL != node.type:
        # Возвращаем токен как элемент списка
        return [node.token.str]

    # Обработка нетерминалов
    result = []

    # Рекурсивная обработка дочерних узлов
    for i in range(len(node.childs)):
        child_code = __GetNodeCode(node.childs[i])
        result.extend(child_code)
    return result


def GetDirect(node):
    result = {"condition": None}
    for child in node.childs:
        text_code = __GetNodeCode(child)
        if not text_code:
            continue
        if len(text_code) == 1:
            result["state_end"] = text_code[0]
            continue
        split_lists = [list(group) for key, group in groupby(text_code, lambda x: x == ';') if not key]
        result["actions"] = [''.join(sublist).strip() for sublist in split_lists]

    if "actions" not in result:
        result["actions"] = None
    return [result]


def GetChoice(node):
    result_all = []
    result = {}
    condition = None
    for child in node.childs:
        text_code = __GetNodeCode(child)
        if child.nonterminalType == dsl_info.Nonterminal.ACTIONS:
            split_lists = [list(group) for key, group in groupby(text_code, lambda x: x == ';') if not key]
            result["actions"] = [''.join(sublist).strip() for sublist in split_lists]
            continue
        if text_code[0] == "[":
            condition = True
            continue
        if text_code[0] == "else":
            if "actions" not in result:
                result["actions"] = None
            result_all.append(result)
            result = {}
        if condition:
            result["condition"] = text_code[0]
            condition = False
            continue
        if text_code[0] in [key[0] for key in dsl_info.keys]:
            continue
        result["end_state"] = text_code[0]
    result_all.append(result)
    return result_all


def __GetState(node):
    # Обработка терминалов
    if TreeNode.Type.NONTERMINAL != node.type:
        # Возвращаем токен как элемент списка
        if node.token.type == Token.Type.TERMINAL:
            return node.token.str
        else:
            return None

    # Обработка нетерминалов
    if node.nonterminalType == dsl_info.Nonterminal.STATE:
        result = {node.childs[0].token.str: [__GetState(node.childs[1])]}
        return result

    current_key = None
    result = {}
    for child in node.childs:
        if child.nonterminalType == dsl_info.Nonterminal.CALL:
            current_key = ''.join(__GetNodeCode(child))
            result[current_key] = {}
            continue
        if child.nonterminalType == dsl_info.Nonterminal.DIRECT:
            result[current_key] = GetDirect(child)
            continue
        if child.nonterminalType == dsl_info.Nonterminal.CHOICE:
            result[current_key] = GetChoice(child)

    return result


def parse_list(list_words):
    dict_word = {}
    if "(" in list_words:
        elements_after_colons = [list_words[i + 1] for i, x in enumerate(list_words) if x == ':']
        dict_word[list_words[0]] = elements_after_colons
    else:
        dict_word[list_words[0]] = []
    return dict_word


def parse_variable(list_words):
    dict_word = {list_words[0]: list_words[-1]}
    return dict_word


def parse_objects(list_words):
    class_name = [list_words[i + 1] for i, x in enumerate(list_words) if x == 'new']
    dict_word = {list_words[0]:
        {
            "class": class_name[0],
            "state": list_words[-2]
        }
    }
    return dict_word


def create_dict(list_words):
    new_list = create_link(list_words)
    return parse_list(new_list)


def create_link(list_words):
    index_ = None
    if "(" in list_words:
        index_ = list_words.index("(")
    if index_:
        return ["".join(list_words[:index_])] + list_words[index_:]
    return ["".join(list_words)]


def parse_links(list_words):
    i = list_words.index('<-')
    dict_sourse = create_dict(list_words[:i])
    dict_target = create_dict(list_words[i+1:])
    dict_sourse.update(dict_target)
    return [dict_sourse]


def parse_public(child, str_command, curr_dict):
    if child.type == TreeNode.Type.TOKEN:
        if child.token.str == "private":
            return False, str_command
        str_command += child.token.str
        return None, str_command
    command = __GetNodeCode(child)
    command.insert(0, str_command)
    curr_dict.extend([create_dict(command)])
    return True, ""


def parse_private(child, str_command, curr_dict):
    if child.type == TreeNode.Type.TOKEN:
        str_command += child.token.str
        return str_command
    command = __GetNodeCode(child)
    command.insert(0, str_command)
    curr_dict.extend([create_dict(command)])
    return ""


def __GetTable(node, current_k=None):
    # Если узел терминальный
    if TreeNode.Type.NONTERMINAL != node.type:
        # Возвращаем токен как элемент списка, если это терминал
        if node.token.type == Token.Type.TERMINAL and current_k:
            return node.token.str
        # Если это ключевое слово, возвращаем его как маркер
        elif node.token.type == Token.Type.KEY:
            if node.token.str in dsl_info.keywords:
                return node.token.str  # Возвращаем ключевое слово
        return None  # Игнорируем остальное

    # Если узел нетерминальный
    result = {}
    current_key = current_k
    current_dict = None
    str_command = ""

    # Обрабатываем дочерние узлы
    for child in node.childs:
        if current_key in ["events", "effects", "conditions", "assertions"]:
            current_dict.update(parse_list(__GetNodeCode(child)))
            continue

        if current_key in ["variables"]:
            current_dict.update(parse_variable(__GetNodeCode(child)))
            continue

        if current_key in ["objects"]:
            current_dict.update(parse_objects(__GetNodeCode(child)))
            continue

        if current_key in ["links"]:
            current_dict.extend(parse_links(__GetNodeCode(child)))
            continue

        if current_key in ["public"]:
            interf, str_command = parse_public(child, str_command, current_dict)
            if interf in [True, None]:
                continue

        if current_key in ["private"]:
            str_command = parse_private(child, str_command, current_dict)
            continue

        if current_key in ["states"]:
            state_dict = __GetState(child)
            state_key = list(state_dict.keys())[0]
            if state_key in current_dict:
                current_dict[state_key].extend(state_dict[state_key])
                continue
            current_dict.update(__GetState(child))
            continue

        child_code = __GetTable(child, current_key)
        if child_code is None:  # Пропускаем пустые результаты
            continue

        # Если это ключевое слово, начинаем новую секцию
        if child_code in dsl_info.keywords:
            current_key = child_code
            if current_key in ["links", "private", "public"]:
                result[current_key] = []
                current_dict = result[current_key]
            elif current_key != "class":
                result[current_key] = {}
                current_dict = result[current_key]
        else:
            # Если текущий ключ есть, добавляем данные в соответствующую секцию
            if current_key:
                if current_key == "class":
                    if isinstance(child_code, str):
                        # Если child_code — это имя класса
                        class_name = child_code
                        if "classes" not in result:
                            result["classes"] = {}
                        result["classes"][class_name] = {}  # Создаем запись для класса
                        current_dict = result["classes"][class_name]
                    else:
                        # Если child_code — это данные класса (events, effects и т.д.)
                        class_name = list(result["classes"].keys())[-1]  # Берем последний добавленный класс
                        result["classes"][class_name].update(child_code)

                elif current_key == "scheme":
                    result["scheme"].update(child_code)
                else:
                    current_key = None
            else:
                if "classes" not in result:
                    result.update(child_code)
                elif "classes" in child_code:
                    result["classes"].update(child_code["classes"])
                else:
                    result.update(child_code)

    return result




def InterpretCode(ast):
    try:
        print("\nПостроение таблиц...")
        table_code = __GetTable(ast)
        import json

        print(json.dumps(table_code, indent=4))

    except RuntimeError as e:
        error_msg = f"Code generation error: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return error_msg

from syntax import *
import dsl_info_ciao as dsl_info
import pprint
from interpretator.createTable import GetTable, create_link
from tabulate import tabulate
import re
from colorama import Fore, init, Style


init(autoreset=True)


def print_table(matrix, headers):
    print(tabulate(matrix, headers, tablefmt="simple_grid", stralign='center'))


class Interpreter:
    class Cell:
        def __init__(self, actions, end_state):
            self.actions = actions
            self.end_state = end_state

        def __str__(self):
            cell_str = f"Actions: {self.actions}, End State: {self.end_state}"
            if hasattr(self, 'condition') and self.condition is not None:
                cell_str += f", Condition: {self.condition}"
            return cell_str

    class Object:
        def __init__(self, classInfo, className, currentState):
            self.clas = className
            self.state = currentState
            if "conditions" in list(classInfo.keys()):
                self.condition = {}
                for cond in classInfo["conditions"]:
                    self.condition[cond] = False
            if "variables" in list(classInfo.keys()):
                self.variables = classInfo["variables"]
                # тут по идее должна быть первичная инициализация какая-то...
            if "assertions" in list(classInfo.keys()):
                self.assertion = classInfo["assertions"]

    def __init__(self, ast):
        self.table_code = GetTable(ast)

        # init classes
        self.events = {}
        self.effects = {}
        self.variables = {}
        self.condition = {}
        self.assertion = {}
        self.classInitialization()
        self.stateTable = self.getStateTable()

        # for clas in list(self.stateTable.keys()):
        #     print_table(self.stateTable[clas][1:], self.stateTable[clas][0])

        # init scheme
        self.objects = {}
        self.links = {}
        if not self.stateTable:
            return

        self.initObject()
        self.initLink()
        self.initInterface()

    def classInitialization(self):
        for clas in list(self.table_code["classes"].keys()):
            self.events[clas] = self.table_code["classes"][clas]["events"]
            if "effects" in list(self.table_code["classes"][clas].keys()):
                self.effects[clas] = self.table_code["classes"][clas]["effects"]
            if "variables" in list(self.table_code["classes"][clas].keys()):
                self.variables[clas] = self.table_code["classes"][clas]["variables"]
            if "conditions" in list(self.table_code["classes"][clas].keys()):
                self.condition[clas] = self.table_code["classes"][clas]["conditions"]
            if "assertions" in list(self.table_code["classes"][clas].keys()):
                self.assertion[clas] = self.table_code["classes"][clas]["assertions"]

    def initObject(self):
        dict_object = self.table_code["scheme"]["objects"]
        classes_init = list(self.table_code["classes"].keys())

        for obj, value in dict_object.items():
            name = value["class"]
            if name not in classes_init:
                print(Fore.RED + f"Класс {name} - не объявлен")
                self.objects = None
                return

            state = value["state"]
            states = [row[0] for row in self.stateTable[name]]
            states = states[1:]
            if state not in states:
                print(Fore.RED + f"Состояние {state} - не объявлено")
                self.objects = None
                return

            self.objects[obj] = self.Object(className=name,
                                            classInfo=self.table_code["classes"][name],
                                            currentState=state)
            print(f"Создан объект {Style.BRIGHT + obj + Style.RESET_ALL} класса {name} в начальном состоянии {state}.")

    def validationLink(self, link):
        objects_init = list(self.objects.keys())
        link_split = link.split('.')
        link_obj = link_split[0]
        if link_obj not in objects_init:
            print(Fore.RED + f"Объект {link_obj} не определён", end=" ")
            self.links = None
            return False

        link_func = link_split[1]
        index_ = None
        if "(" in link_func:
            index_ = link_func.index("(")
        if index_:
            link_list = ["".join(link_func[:index_])] + [link_func[index_:]]
        else:
            link_list = ["".join(link_func)]
        link_dict = {}
        if "(" in link_func:
            elements_after_colons = re.findall(r":([^,)]+)", link_list[1])
            link_dict[link_list[0]] = elements_after_colons
        else:
            link_dict[link_list[0]] = []

        class_obj = self.objects[link_obj].clas
        if link_dict.items() <= self.events[class_obj].items():
            return True
        if class_obj in self.effects:
            if link_dict.items() <= self.effects[class_obj].items():
                return True
        if class_obj in self.condition:
            if link_dict.items() <= self.condition[class_obj].items():
                return True
        if class_obj in self.assertion:
            if link_dict.items() <= self.assertion[class_obj].items():
                return True

        print(Fore.RED + f"Ошибка в {link_func}", end=" ")
        return False

    def validationInterface(self, interface, var_type):
        objects_init = list(self.objects.keys())
        interface_split = interface.split('.')
        interface_obj = interface_split[0]
        if interface_obj not in objects_init:
            print(Fore.RED + f"Объект {interface_obj} не определён", end=" ")
            self.links = None
            return False

        interface_func = interface_split[1]

        interface_dict = {interface_func: var_type}

        class_obj = self.objects[interface_obj].clas
        if interface_dict.items() <= self.events[class_obj].items():
            return True
        if class_obj in self.effects:
            if interface_dict.items() <= self.effects[class_obj].items():
                return True
        if class_obj in self.condition:
            if interface_dict.items() <= self.condition[class_obj].items():
                return True
        if class_obj in self.assertion:
            if interface_dict.items() <= self.assertion[class_obj].items():
                return True

        print(Fore.RED + f"Ошибка в {interface_func}", end=" ")
        return False

    def initLink(self):
        self.links = self.table_code["scheme"]["links"]
        print()
        for link in self.links:
            for key, value in link.items():
                if not self.validationLink(key):
                    print(Fore.RED + f"в связи {key} <- {value}")
                    self.links = None
                    return
                if not self.validationLink(value):
                    print(Fore.RED + f"в связи {key} <- {value}")
                    self.links = None
                    return
                print("Установлена связь " + Style.BRIGHT + f"{key} <- {value}")
        print()

    def initInterface(self):
        if "public" in self.table_code["scheme"]:
            self.public = self.table_code["scheme"]["public"]
            for interface in self.public:
                for key, value in interface.items():
                    if not self.validationInterface(key, value):
                        print(Fore.RED + f"в интерфейсе public: {key}")
                        self.public = None
                        return
        if "private" in self.table_code["scheme"]:
            self.private = self.table_code["scheme"]["private"]
            for interface in self.private:
                for key, value in interface.items():
                    if not self.validationInterface(key, value):
                        print(Fore.RED + f"в интерфейсе public: {key}")
                        self.private = None
                        return

    def validation(self):
        if not self.stateTable:
            return False
        if not self.objects:
            return False
        if not self.links:
            return False
        if hasattr(self, "public"):
            if not self.public:
                return False
        if hasattr(self, "private"):
            if not self.private:
                return False
        return True

    def validateAct(self, actions, clas):
        if actions is None:
            return True
        for act in actions:
            if not self.checkVariable(act, clas):
                print(Fore.RED + f"Ошибка в {clas} - {act}",end=" ")
                return False
        return True

    def createCell(self, valueState, clas):
        if len(valueState) == 1:
            cell = self.Cell(actions=valueState[0]["actions"], end_state=valueState[0]["end_state"])
            return cell
        actions = []
        end_states = []
        for value in valueState:
            if not self.validateAct(value["actions"], clas):
                return None
            actions.append(value["actions"])
            end_states.append(value["end_state"])

        cell = self.Cell(actions=actions, end_state=end_states)
        condition = valueState[0]["condition"]
        if not self.checkVariable(condition, clas):
            print(Fore.RED + f"Ошибка в условии в {clas} {condition}", end=" ")
            return None
        cell.condition = condition
        return cell

    def checkVariable(self, event_name, clas):
        event = event_name
        if "(" in event_name:
            ind_start = event_name.index("(")
            ind_end = event_name.index(")")
            event = event_name[:ind_start]
            variablesList = event_name[ind_start + 1:ind_end]
            if "," in variablesList:
                variables = variablesList.split(',')
            else:
                variables = [variablesList]
        else:
            variables = []

        var_type = []
        for var in variables:
            typeV = None
            for varCl, varType in self.variables[clas].items():
                if var == varCl:
                    typeV = varType
                    break
            if not typeV:
                print(Fore.RED + f"Используется необъвленная переменная")
                return False
            var_type.append(typeV)

        reservfunc = list(dsl_info.reserved_func.keys())
        types_var_ev = []
        if event in reservfunc:
            types_var_ev = dsl_info.reserved_func[event]
        elif event in self.events[clas]:
            types_var_ev = self.events[clas][event]
        elif event in self.effects[clas]:
            types_var_ev = self.effects[clas][event]
        elif event in self.condition[clas]:
            types_var_ev = self.condition[clas][event]
        elif event in self.assertion[clas]:
            types_var_ev = self.assertion[clas][event]

        if var_type == types_var_ev:
            return True

        if not types_var_ev:
            print(Fore.RED + "Не принимает аргументы")
        else:
            print(Fore.RED + "Неправильные типы переданных переменных")
        return False

    def createStateMatrix(self, events, states, clas):
        col_name = [""]
        col_name.extend(events)
        col_size = len(col_name)
        row_size = len(states)
        matrix = [[None for _ in range(col_size)] for _ in range(row_size)]
        matrix.insert(0, col_name)
        for i, state in enumerate(states):
            matrix[i + 1][0] = state
            for j in range(len(states[state])):
                event_name = list(states[state][j].keys())[0]
                # добавить проверку на соответсвие типов передаваемых variables
                ev_name = event_name
                if not self.checkVariable(event_name, clas):
                    print(Fore.RED + f"Ошибка в {clas} {state} {event_name}")
                    return None
                if "(" in event_name:
                    ind_b = event_name.index("(")
                    ev_name = event_name[:ind_b]

                if ev_name in col_name:
                    ind = col_name.index(ev_name)
                else:
                    reservfunc = list(dsl_info.reserved_func.keys())
                    if ev_name not in reservfunc:
                        print(Fore.RED + "Недопустимое событие")
                        return None
                    for row in matrix:
                        row.append(None)
                    ind = len(matrix[0]) - 1
                    matrix[0][ind] = ev_name
                cell = self.createCell(states[state][j][event_name], clas)
                if cell is None:
                    print(Fore.RED + f" в {state}")
                    return None
                matrix[i + 1][ind] = cell
        # print(matrix)
        return matrix

    def getStateTable(self):
        state_table = {}
        classes = list(self.table_code["classes"].keys())
        for clas in classes:
            events = list(self.table_code["classes"][clas]["events"].keys())
            states = self.table_code["classes"][clas]["states"]
            stateMatrix = self.createStateMatrix(events, states, clas)
            if not stateMatrix:
                return None
            state_table[clas] = stateMatrix
        return state_table

    def interpretActions(self, obj, actions):
        for act in actions:
            print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> Выполнение действия: {Style.BRIGHT + act + Style.RESET_ALL}...")
            link_act = f"{obj}.{act}"
            for link in self.links:
                for key, value in link.items():
                    if link_act not in key:
                        continue
                    event_link = value
                    parts = event_link.split('.')
                    print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
                          f"Событие {Style.BRIGHT + parts[1] + Style.RESET_ALL} "
                          f"отправлено объекту {Style.BRIGHT + parts[0] + Style.RESET_ALL}\n")
                    self.interpret(event_link, False)
                    break

            print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> Действие: {Style.BRIGHT + act + Style.RESET_ALL} "
                  f"- выполнено")

    def interpret(self, interface, isUser):
        parts = interface.split('.')
        if len(parts) != 2:
            print(Fore.RED + "Некорректно введено событие. Вид: объект.событие")
            return

        if isUser:
            reservfunc = list(dsl_info.reserved_func.keys())
            ev = parts[1]
            if "(" in ev:
                ind_b = ev.index("(")
                ev = ev[:ind_b]
            if ev in reservfunc:
                print(Fore.RED + "Введено зарезервированное состояние недоступное пользователю")
                return
            res = True
            if hasattr(self, "public"):
                public_interface = [list(interf.keys())[0] for interf in self.public]
                res = interface in public_interface
            if not res:
                if hasattr(self, "private"):
                    private_interface = [list(interf.keys())[0] for interf in self.private]
                    res = interface in private_interface
            if not res:
                print(Fore.RED + "Введена недопустимая команда. Повторите ещё раз")
                return
        obj = parts[0]
        event = parts[1]
        print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
              f"Выполнение события {Style.BRIGHT + event + Style.RESET_ALL}...")
        if "(" in event:
            ind_b = event.index("(")
            event = event[:ind_b]

        autoClass = self.objects[obj]
        clas = autoClass.clas

        state_table = self.stateTable[clas]
        state_name = [row[0] for row in state_table]

        ind_event = state_table[0].index(event)
        ind_state = state_name.index(autoClass.state)
        cell = state_table[ind_state][ind_event]

        if not cell:
            print("Состояния не могут быть изменены, задайте другое событие")
            for obj in list(self.objects.keys()):
                print(f">> {obj}:{self.objects[obj].state}")
            print()
            return

        if hasattr(cell, "condition"):
            # посмотреть как учитывать условия в виде математического выражения
            if not autoClass.condition:
                print(Fore.RED + f"Класс не содержит условий. Проверьте код")
                return

            if cell.condition not in list(autoClass.condition.keys()):
                print(Fore.RED + f"Недопустимое условие")
                return

            print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
                  f"Проверка условия: {Style.BRIGHT + cell.condition + Style.RESET_ALL} "
                  f"= {autoClass.condition[cell.condition]}")
            if autoClass.condition[cell.condition]:
                autoClass.condition[cell.condition] = False
                end_state = cell.end_state[0]
                actions = cell.actions[0]
            else:
                autoClass.condition[cell.condition] = True
                end_state = cell.end_state[1]
                actions = cell.actions[1]

        else:
            end_state = cell.end_state
            actions = cell.actions

        if actions:
            self.interpretActions(obj, actions)

        print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
              f"Переход: {Style.BRIGHT + autoClass.state + Style.RESET_ALL} -> "
              f"{Style.BRIGHT + end_state + Style.RESET_ALL}")
        autoClass.state = end_state
        print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> Cобытиe: {Style.BRIGHT + event + Style.RESET_ALL} "
              f"- выполнено\n")

    def print_command(self, interface):
        for key, value in interface.items():
            if not value:
                print(f"{Style.BRIGHT + key + Style.RESET_ALL}")
                continue
            variable = ""
            for i in range(len(value)):
                if i == len(value) - 1:
                    variable += f"t{i}: {value[i]}"
                    continue
                variable += f"t{i}: {value[i]}, "
            print(Style.BRIGHT + f"{key}({variable})" + Style.RESET_ALL)

    def available_commands(self):
        if "public" in self.table_code["scheme"]:
            for interface in self.public:
                self.print_command(interface)

        if "private" in self.table_code["scheme"]:
            for interface in self.public:
                self.print_command(interface)

    def handle_command(self, command):
        if command == "":
            return True
        if command == "exitCode":
            print("Завершение текущей программы.")
            return False
        if command == "help":
            print("Доступные команды:")
            print(Fore.GREEN + "  exitCode - завершить текущую программу")
            print(Fore.GREEN + "  interfaces - получить список доступных интерфейсов")
            return True
        if command == "interfaces":
            print("Доступные интерфейсы:")
            self.available_commands()
            return True
        self.interpret(command, True)
        return True


def InterpretCode(ast):
    try:
        # print("\nПостроение таблиц...")
        print("\nЗапуск интерпретатора...\n")
        print("Команда: " + Fore.GREEN + "help" + Fore.RESET + " - показать список команд\n")
        inter = Interpreter(ast)
        if not inter.validation():
            return

        while True:
            command = input(">>> ").strip()
            command = command.replace(">>>", "")
            if not inter.handle_command(command):
                break

    except RuntimeError as e:
        error_msg = f"Code generation error: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return

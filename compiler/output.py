# Сгенерированный код на Python из программы CIAO 3
import random
import inspect
import threading


class ResettableTimer:
    def __init__(self, parent_class, interval, function):
        self.parent_class = parent_class
        self.interval = interval    # Время ожидания в секундах
        self.function = function    # Функция для выполнения
        self.timer = None           # Ссылка на объект таймера
        self.is_running = False     # Флаг состояния таймера

    def _start_timer(self):
        # Внутренний метод для запуска таймера
        self.timer = threading.Timer(self.interval, self._on_complete)
        self.timer.start()
        self.is_running = True

    def _on_complete(self):
        # Вызывается по истечении времени
        self.is_running = False
        self.function(self.parent_class)

    def start(self):
        # Запуск или перезапуск таймера
        if self.is_running:
            self.timer.cancel()
        self._start_timer()

    def reset(self):
        # Сброс и перезапуск таймера
        self.start()

    def cancel(self):
        # Полная отмена таймера
        if self.is_running:
            self.timer.cancel()
            self.is_running = False
            

class Device:
    def __init__(self, init_state):
        self.state = init_state
        self.state_machine = self.build_state_machine()
        self.timers = self.build_timers()
        self.timer = None
        self.links = {}
        print(f"Device инициализирован с состоянием {init_state}")
        self.name = "Device"

    def addLink(self, name: str, func) -> None:
        self.links[name] = func

    def Off(self):
        print("Device: Event Off()")
        event = "Off"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Off' in self.links:
            self.links['Off']()

    def On(self):
        print("Device: Event On()")
        event = "On"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'On' in self.links:
            self.links['On']()

    def IsOn(self):
        return self.state == "On"

    def build_state_machine(self):
        state_machine = {}
        if 'Off' not in state_machine:
            state_machine['Off'] = {}
        state_machine['Off']['On'] = (lambda self: (self.change_state('On'), self.check_timer()))
        if 'Off' not in state_machine:
            state_machine['Off'] = {}
        state_machine['Off']['Off'] = (lambda self: (self.change_state('Off'), self.check_timer()))
        if 'On' not in state_machine:
            state_machine['On'] = {}
        state_machine['On']['On'] = (lambda self: (self.change_state('On'), self.check_timer()))
        if 'On' not in state_machine:
            state_machine['On'] = {}
        state_machine['On']['Off'] = (lambda self: (self.change_state('Off'), self.check_timer()))
        return state_machine

    def build_timers(self):
        timers = {}
        return timers

    def change_state(self, new_state):
        if self.timer:
            self.timer.cancel()
        print(f"{self.__class__.__name__}: смена состояния {self.state} -> {new_state}")
        self.state = new_state

    def check_timer(self):
        if self.state in self.timers:
            self.timer = ResettableTimer(self, getattr(self, self.timers[self.state]), self.state_machine[self.state]['After'])
            self.timer.start()

class Controller:
    def __init__(self, init_state):
        self.t1 = None  # type: Integer
        self.t2 = None  # type: Integer
        self.state = init_state
        self.state_machine = self.build_state_machine()
        self.timers = self.build_timers()
        self.timer = None
        self.links = {}
        print(f"Controller инициализирован с состоянием {init_state}")
        self.name = "Controller"

    def addLink(self, name: str, func) -> None:
        self.links[name] = func

    def In(self):
        print("Controller: Event In()")
        event = "In"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'In' in self.links:
            self.links['In']()

    def Out(self):
        print("Controller: Event Out()")
        event = "Out"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Out' in self.links:
            self.links['Out']()

    def Enter(self):
        print("Controller: Event Enter()")
        event = "Enter"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Enter' in self.links:
            self.links['Enter']()

    def Exit(self):
        print("Controller: Event Exit()")
        event = "Exit"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Exit' in self.links:
            self.links['Exit']()

    def Open_door(self):
        print("Controller: Effect Open_door вызван")
        if 'Open_door' in self.links:
            self.links['Open_door']()

    def Close_door(self):
        print("Controller: Effect Close_door вызван")
        if 'Close_door' in self.links:
            self.links['Close_door']()

    def Switch_on(self):
        print("Controller: Effect Switch_on вызван")
        if 'Switch_on' in self.links:
            self.links['Switch_on']()

    def Switch_off(self):
        print("Controller: Effect Switch_off вызван")
        if 'Switch_off' in self.links:
            self.links['Switch_off']()

    def Occupy(self):
        print("Controller: Effect Occupy вызван")
        if 'Occupy' in self.links:
            self.links['Occupy']()

    def Free(self):
        print("Controller: Effect Free вызван")
        if 'Free' in self.links:
            self.links['Free']()

    def Occupied(self):
        if "Occupied" in self.links:
            result = self.links['Occupied']()
        else:
            result = random.choice([True, False])
        print("Condition Occupied() =>", result)
        return result

    def build_state_machine(self):
        state_machine = {}
        if 'Idle' not in state_machine:
            state_machine['Idle'] = {}
        state_machine['Idle']['In'] = (lambda self: (self.change_state('Idle'), self.check_timer()) if self.Occupied() else (self.change_state('I2B'), setattr(self, 't1', 5), setattr(self, 't2', 5), self.Switch_on(), self.Open_door(), self.check_timer()))
        if 'I2B' not in state_machine:
            state_machine['I2B'] = {}
        state_machine['I2B']['After'] = (lambda self: (self.change_state('Idle'), self.Close_door(), self.Switch_off(), self.check_timer()))
        if 'I2B' not in state_machine:
            state_machine['I2B'] = {}
        state_machine['I2B']['Enter'] = (lambda self: (self.change_state('Busy'), self.Close_door(), self.Occupy(), self.check_timer()))
        if 'Busy' not in state_machine:
            state_machine['Busy'] = {}
        state_machine['Busy']['Out'] = (lambda self: (self.change_state('B2I'), self.Open_door(), self.check_timer()))
        if 'B2I' not in state_machine:
            state_machine['B2I'] = {}
        state_machine['B2I']['After'] = (lambda self: (self.change_state('Busy'), self.Close_door(), self.check_timer()))
        if 'B2I' not in state_machine:
            state_machine['B2I'] = {}
        state_machine['B2I']['Exit'] = (lambda self: (self.change_state('Idle'), self.Close_door(), self.Switch_off(), self.Free(), self.check_timer()))
        return state_machine

    def build_timers(self):
        timers = {}
        timers["I2B"] = "t1"
        timers["B2I"] = "t2"
        return timers

    def change_state(self, new_state):
        if self.timer:
            self.timer.cancel()
        print(f"{self.__class__.__name__}: смена состояния {self.state} -> {new_state}")
        self.state = new_state

    def check_timer(self):
        if self.state in self.timers:
            self.timer = ResettableTimer(self, getattr(self, self.timers[self.state]), self.state_machine[self.state]['After'])
            self.timer.start()

def run(*args):
    for obj in args:
        try:
            obj.In()
        except Exception as e:
            pass

def main():
    controller = Controller('Idle')
    door = Device('Off')
    light = Device('Off')
    cabin = Device('Off')
    controller.addLink('Open_door', door.On)
    controller.addLink('Close_door', door.Off)
    controller.addLink('Switch_on', light.On)
    controller.addLink('Switch_off', light.Off)
    controller.addLink('Occupy', cabin.On)
    controller.addLink('Free', cabin.Off)
    controller.addLink('Occupied', cabin.IsOn)
    run(controller, door, light, cabin)

if __name__ == '__main__':
    main()
    # Функция run доступна, но не вызывается автоматически
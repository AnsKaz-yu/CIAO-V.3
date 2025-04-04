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
            

class TrafficLight:
    def __init__(self, init_state):
        self.t1 = None  # type: Integer
        self.t2 = None  # type: Integer
        self.state = init_state
        self.state_machine = self.build_state_machine()
        self.timers = self.build_timers()
        self.timer = None
        self.links = {}
        print(f"TrafficLight инициализирован с состоянием {init_state}")
        self.name = "TrafficLight"

    def addLink(self, name: str, func) -> None:
        self.links[name] = func

    def Switch(self):
        print("TrafficLight: Event Switch()")
        event = "Switch"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Switch' in self.links:
            self.links['Switch']()

    def OnGreen(self):
        print("TrafficLight: Event OnGreen()")
        event = "OnGreen"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'OnGreen' in self.links:
            self.links['OnGreen']()

    def OnRed(self):
        print("TrafficLight: Event OnRed()")
        event = "OnRed"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'OnRed' in self.links:
            self.links['OnRed']()

    def Stop(self):
        print("TrafficLight: Event Stop()")
        event = "Stop"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Stop' in self.links:
            self.links['Stop']()

    def To_green(self):
        print("TrafficLight: Effect To_green вызван")
        if 'To_green' in self.links:
            self.links['To_green']()

    def To_red(self):
        print("TrafficLight: Effect To_red вызван")
        if 'To_red' in self.links:
            self.links['To_red']()

    def build_state_machine(self):
        state_machine = {}
        if 'Idle' not in state_machine:
            state_machine['Idle'] = {}
        state_machine['Idle']['Switch'] = (lambda self: (self.change_state('Red'), setattr(self, 't1', 20), setattr(self, 't2', 10), self.check_timer()))
        if 'Red' not in state_machine:
            state_machine['Red'] = {}
        state_machine['Red']['After'] = (lambda self: (self.change_state('Red'), self.To_green(), self.check_timer()))
        if 'Red' not in state_machine:
            state_machine['Red'] = {}
        state_machine['Red']['OnGreen'] = (lambda self: (self.change_state('Green'), self.check_timer()))
        if 'Red' not in state_machine:
            state_machine['Red'] = {}
        state_machine['Red']['Stop'] = (lambda self: (self.change_state('Idle'), self.check_timer()))
        if 'Green' not in state_machine:
            state_machine['Green'] = {}
        state_machine['Green']['After'] = (lambda self: (self.change_state('Green'), self.To_red(), self.check_timer()))
        if 'Green' not in state_machine:
            state_machine['Green'] = {}
        state_machine['Green']['OnRed'] = (lambda self: (self.change_state('Red'), self.check_timer()))
        if 'Green' not in state_machine:
            state_machine['Green'] = {}
        state_machine['Green']['Stop'] = (lambda self: (self.change_state('Idle'), self.check_timer()))
        return state_machine

    def build_timers(self):
        timers = {}
        timers["Red"] = "t1"
        timers["Green"] = "t2"
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
            obj.Switch()
            obj.Stop()
        except Exception as e:
            pass

def main():
    traffic_light = TrafficLight('Idle')
    traffic_light.addLink('To_green', traffic_light.OnGreen)
    traffic_light.addLink('To_red', traffic_light.OnRed)

if __name__ == '__main__':
    main()
    # Функция run доступна, но не вызывается автоматически
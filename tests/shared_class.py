from multiprocessing import Manager, Process
from multiprocessing.managers import BaseManager


# custom manager to support custom classes
class CustomManager(BaseManager):
    # nothing
    pass


# Класс, который будет общим между процессами
class SharedClass:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def get_value(self):
        return self.value


# Функция для процесса, которая использует общий объект
def process_task(shared_obj, process_id):
    for _ in range(20):
        shared_obj.increment()
        print(f"Process {process_id}: {shared_obj.get_value()}")


if __name__ == "__main__":
    # Создаем менеджер для управления общими объектами
    CustomManager.register("SharedClass", SharedClass)
    manager = CustomManager()
    manager.start()

    # Создаем общий объект класса
    shared_obj = manager.__getattribute__("SharedClass")()
    print(type(shared_obj))

    # Создаем процессы
    process1 = Process(target=process_task, args=(shared_obj, 1))
    process2 = Process(target=process_task, args=(shared_obj, 2))

    # Запускаем процессы
    process1.start()
    process2.start()

    # Ожидаем завершения процессов
    process1.join()
    process2.join()

    # Выводим финальное значение
    print(f"Final value: {shared_obj.get_value()}")

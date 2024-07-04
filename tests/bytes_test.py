import multiprocessing
from io import BytesIO
from time import sleep


def worker(queue):
    sleep(1)
    received_obj = queue.get()  # Получаем объект из очереди
    print("Worker received object with content:", received_obj.getvalue())


if __name__ == "__main__":
    # Создаем очередь
    queue = multiprocessing.Queue()

    # Создаем объект BytesIO и записываем в него данные
    buffer = BytesIO()
    buffer.write(b"This is some binary data")

    # Помещаем объект BytesIO в очередь
    queue.put(buffer)

    # Изменяем исходные данные после помещения в очередь
    # buffer.seek(0)
    buffer.write(b"New data")

    # Запускаем процесс
    process = multiprocessing.Process(target=worker, args=(queue,))
    process.start()
    process.join()

    # Проверяем содержимое исходного объекта
    buffer.seek(0)
    print("Main process object content:", buffer.getvalue())

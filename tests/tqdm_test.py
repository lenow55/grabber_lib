from tqdm import tqdm
import time
import threading


# Пример функции, имитирующей задачу
def task(duration, bar):
    for _ in range(duration):
        time.sleep(0.1)
        bar.update(1)


if __name__ == "__main__":
    total_steps_1 = 100
    total_steps_2 = 150

    # Создайте два progress bar с различными позициями и настройками
    bar1 = tqdm(
        total=total_steps_1,
        desc="Task 1",
        position=0,
        dynamic_ncols=True,
        leave=True,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        colour="green",
    )
    bar2 = tqdm(
        total=total_steps_2,
        desc="Task 2",
        position=1,
        dynamic_ncols=True,
        leave=True,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        colour="red",
    )

    # Создайте потоки для выполнения задач
    thread1 = threading.Thread(target=task, args=(total_steps_1, bar1))
    thread2 = threading.Thread(target=task, args=(total_steps_2, bar2))

    # Запустите потоки
    thread1.start()
    thread2.start()

    # Ожидайте завершения потоков
    thread1.join()
    thread2.join()

    # Закройте progress bar
    bar1.close()
    bar2.close()

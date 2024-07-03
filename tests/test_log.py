import logging
import logging.handlers
import multiprocessing
import time
from logging import config as logging_config


def log_listener(queue, log_config):
    """
    Процесс слушателя, который будет записывать логи в файл
    """
    logging_config.dictConfig(log_config)
    logger = logging.getLogger()

    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger.handle(record)
        except Exception:
            import sys
            import traceback

            print("Ошибка при записи лога:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def log_worker_config(queue):
    """
    Настройка логгера для рабочих процессов
    """
    h = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG)


def worker_process(queue, worker_id):
    """
    Пример рабочего процесса, который генерирует логи
    """
    log_worker_config(queue)
    logger = logging.getLogger(__name__)
    logger.info(f"Процесс {worker_id} начал работу.")
    time.sleep(2)
    logger.info(f"Процесс {worker_id} завершил работу.")


if __name__ == "__main__":
    # Настройка логирования
    log_config = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": "multiprocessing_log.log",
                "formatter": "default",
                "mode": "w",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["file"]},
    }

    log_queue = multiprocessing.Queue()
    listener = multiprocessing.Process(
        target=log_listener, args=(log_queue, log_config)
    )
    listener.start()

    # Создание и запуск рабочих процессов
    processes = []
    for i in range(5):
        p = multiprocessing.Process(target=worker_process, args=(log_queue, i))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Остановить логгер
    log_queue.put(None)
    listener.join()

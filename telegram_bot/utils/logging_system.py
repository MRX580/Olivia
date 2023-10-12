import logging


def logging_to_file(log_type, *args):
    log_file = 'bot.log'  # Имя файла для записи логов

    # Сопоставление типов логов и уровней логирования
    log_levels = {'warn': logging.WARNING, 'info': logging.INFO, 'error': logging.ERROR}

    # Проверяем, что переданный тип лога допустим
    if log_type not in log_levels:
        raise ValueError("Недопустимый тип лога: должен быть 'warn', 'info' или 'error'.")

    # Конфигурируем логирование
    logging.basicConfig(filename=log_file, level=log_levels[log_type],
                               format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

    # Записываем логи
    for message in args:
        logging.log(log_levels[log_type], message)
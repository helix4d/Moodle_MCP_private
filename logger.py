import logging
from pathlib import Path
from typing import Optional, Union

def setup_logger(
    name: str,
    logfile: Union[str, Path],
    level: int = logging.INFO,
    mode: str = "a",
    fmt: str = "%(asctime)s - %(levelname)s - %(message)s",
    datefmt: Optional[str] = None,
) -> logging.Logger:
    """
    Настраивает логгер с консольным и файловым хендлерами.

    :param name: имя логгера (logging.getLogger(name))
    :param logfile: путь к файлу лога (может быть str или pathlib.Path)
    :param level: уровень логирования для обоих хендлеров
    :param mode: режим открытия файла ('w' или 'a')
    :param fmt: формат строки лога
    :param datefmt: формат даты (по умолчанию None, т. е. ISO)
    :return: настроенный объект logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # общий форматтер
        formatter = logging.Formatter(fmt, datefmt)

        # консольный хендлер
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # файловый хендлер (директорию создаём при необходимости)
        logfile = Path(logfile)
        logfile.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(logfile, mode=mode, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

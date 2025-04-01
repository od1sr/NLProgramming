from src.outputHandler import OutputHandler
from pathlib import Path
from loguru import logger
from io import StringIO

if __name__ == '__main__':
    buffer = StringIO()
    logger.add(buffer)

    # печатаем всякую хуйню (только через loguru!!!! print не работает)

    buffer.getvalue() # получаем напечатанное, очищаем буфер

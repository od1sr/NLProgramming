from executor import Executor
from config import Language
import subprocess

if __name__ == "__main__":
    task = "Напиши простейшую нейросеть, которая получает слово и возвращает рифму."
    language = Language.PYTHON
    save_path = "game"
    executor = Executor(task, language, save_path)
    executor.generate()
    executor.execute_program()
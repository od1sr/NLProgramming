from executor import Executor
from config import Language
import subprocess

if __name__ == "__main__":
    task = "Напиши простейшую 3d рей-кастинг игру в консоли."
    language = Language.CPP
    save_path = "game"
    executor = Executor(task, language, save_path)
    executor.execute()
    
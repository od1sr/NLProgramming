from executor import Executor
from config import Language


if __name__ == "__main__":
    task = "Напиши программу, которая пишет 'Hello, World!' в консоль."
    language = Language.PYTHON
    save_path = "generated_code"
    executor = Executor(task, language, save_path)
    executor.execute()
    print(executor.code)
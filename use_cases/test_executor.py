from src.executor import Executor
from src.config import Language


if __name__ == "__main__":
    # task = "Напиши простейшую нейросеть, которая получает получает "
    # "последовательность из 5 чисел, "
    # "находит закономерность и пишет в консоль ещё 5 вариантов."
    # language = Language.PYTHON
    # save_path = "generated_code"
    # executor = Executor(task, language)
    # executor.generate()
    # executor.install_dependecies()
    # executor.save_code(save_path)
    # executor.execute_program()
    
    executor = Executor('fsdf', Language.PYTHON)

    executor._Executor__dependecies = [
        'pip install aiogram',
        'sudo dnf install python'
    ]

    #g = executor.install_dependecies()
    for command in executor.install_dependecies():
        print(f'"{command}"')
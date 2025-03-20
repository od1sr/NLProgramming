import subprocess
import re
from pathlib import Path
from .config import GEMINI_API_KEY, Language, proxy, compillable
import requests
import json
import platform
from . import exceptions as exc
from loguru import logger

class Executor:
    '''
    Handles the execution of code generated by Gemini.

    Usage example:
    ```python
        task = "Напиши простейшую нейросеть, которая получает "
            "получает последовательность из 5 чисел, находит"
            "закономерность и пишет в консоль ещё 5 вариантов."
        language = Language.PYTHON
        save_path = "generated_code"
        executor = Executor(task, language)
        executor.generate()
        executor.install_dependecies()
        executor.save_code(save_path)
        executor.execute_program()
    ```
    '''

    def __init__(self, task: str, language: Language):
        '''
        Arguments:
        - task: The description of the program to be executed.
        - language: The programming language of the generated code.
        - save_path: The path where the generated code will be saved.
        '''

        self.task = task
        self.language = language
        self.__save_path = None
        self.__code = self.__full_response = None
        self.__dependecies = None

        self.__saved: bool = False

    @property
    def path(self) -> Path:
        '''The path where the generated code will be saved'''
        return self.__save_path

    @property
    def saved(self) -> bool:
        return self.__saved
        
    @property
    def code(self) -> str:
        '''The program code'''
        return self.__code

    @property
    def dependecies(self) -> list[str] | None:
        '''The list of programs that should be run to install all the dependecies'''
        return self.__dependecies
    
    @property
    def full_response(self) -> str:
        '''The full response from Gemini including code'''
        return self.__full_response
    
    def generate(self):
        '''Sends the task to AI and extracts code and dependecies'''

        self.__full_response = self._send_prompt_to_gemini()
        self.__dependecies = self._extract_code_and_commands()

    def _send_prompt_to_gemini(self) -> str:
        '''Tryes to send the prompt to Gemini and get response.
        If something goes wrong, raises one of the following:
         - exceptions.NetworkError
         - exceptions.CantGetResponseFromAI

        Returns: str: The full response from Gemini
        '''

        prompt = f"{self.task}\n\nПрограмма должна быть написана на {self.language.value}. " + \
            ("Перечисли все комманды, которые необходимо исполнить в терминале, чтобы УСТАНОВИТЬ " \
                "для неё необходимые зависимости."\
                if self.language in (Language.PYTHON, Language.JAVASCRIPT) else ''\
            ) + \
            f"Я использую {platform.system()} {platform.release()}. " \
            "Не надо отправлять комманды для заполнения файла main, компиляции и запуска, я сам скопирую тот код, " \
            "В коде не должно быть комментариев," \
            "который ты пришлёшь, вставлю в файл и запущу. Не надо объяснять код. Просто отправь код и комманды для " \
            "установки библиотек (если они есть). Код должен быть написан так, чтобы программа запустилась сразу без "\
            "дополнительного редактирования. "
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro-exp-02-05:generateContent?key="+\
            GEMINI_API_KEY
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
        }

        logger.info('Sending request to Gemini...')
        try:
            response = requests.post(url, headers=headers, json=payload, proxies=proxy, timeout=120)
            response.raise_for_status()  # Проверка на ошибки HTTP
        except requests.exceptions.ProxyError:
            logger.opt(exception=True).error("Proxy error")
            raise exc.NetworkError()
        except requests.exceptions.RequestException:
            logger.opt(exception=True).error("To Many Requests")
            raise exc.ToManyRequests()
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.opt(exception=True).error("Response handling error")
            raise exc.CantGetResponseFromAI()

        self.__full_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        
        if not self.__full_response:
            logger.error('Response did not contain any text.')
            raise exc.CantGetResponseFromAI('Нихуя не получилось')

        logger.info('Gemini responsed:\n' + self.__full_response)
        
        return self.__full_response
    
    def _extract_code_and_commands(self) -> list[str]:
        '''Extracts code blocks that match the following format:
            ```<language>
                code block
                ...
            ```
        '''

        # exctract code block
        code_match = self._extract_code_blocks_from_text_with_regex(self.language.value)
        if code_match:
            self.__code = code_match[0].strip()
            logger.info(self.__code)
        else:
            raise exc.CantExtractCode()

        dependecies = None    
        if self.language in (Language.PYTHON, Language.JAVASCRIPT):
            # Extract commands to install dependecies
            dependecies = self._extract_code_blocks_from_text_with_regex('bash')

            if dependecies:
                dependecies = [
                    i.strip().split('#')[0] # split('#')[0] is for getting rid of comments
                        for i in '\n'.join(dependecies).split('\n')
                ]
                dependecies = [i for i in dependecies if i]
                logger.info(f'{dependecies}')

        return dependecies

    def _extract_code_blocks_from_text_with_regex(self, language: str) -> list[str]:
        '''Extract code using regex'''

        # convert language name to markdown format
        lang = language.replace('+', 'p').replace('#', 'sharp')
        if lang == Language.JAVASCRIPT.value:
            lang = 'js'

        # makrdown code formatting in regex, using ecranised basic lanugage name as the second variant 
        # (cpp|c\+\+, csharp|c#)
        pattern = r"^```(?:" + f'{lang}|{re.escape(language)}' + r")\n([\s\S]*?)```$"

        return re.findall(pattern, self.__full_response, re.DOTALL | re.IGNORECASE | re.MULTILINE)

    def save_code(self, path: str | Path):
        '''Saves extracted code from AI to the path'''

        extension = {
            Language.PYTHON: '.py',
            Language.CPP: '.cpp',
            Language.JAVASCRIPT: '.js',
        }.get(self.language, '.txt')
        
        self.__save_path = Path(path) / f"main{extension}"
        self.__save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.__save_path, 'w', encoding="UTF-8") as f:
            f.write(self.__code)
            self.__saved = True

    def install_dependecies(self):
        for command in self.__dependecies:
            if not command:
                continue

            try:
                logger.info('RUNNING ' + command)
                subprocess.run(command.split(), check=False)
            except:
                logger.opt(exception=True).error(f"Failed to execute {command}")

    def build_program(self):
        prog_path = ''
        if self.language in compillable:
            prog_path = "main"

            prog_path += {
                Language.CPP: '.exe' if platform.system() == "Windows" else '',
            }.get(self.language)

            prog_path = self.__save_path.parent / prog_path

            compille_command = {
                Language.CPP: f'g++ -o {prog_path} {self.__save_path}',
            }

            try:
                logger.info('COMPILING...')
                subprocess.run(compille_command[self.language].split(), check=False)
            except:
                logger.opt(exception=True).error(f"Failed to compile {self.language} {prog_path}")
                raise exc.CantCompileProgram()
            return prog_path
        return self.__save_path

    def execute_program(self):
        prog_path = self.build_program()
        execute_command = {
            Language.PYTHON: 'python {}',
            Language.CPP: '{}',
            Language.JAVASCRIPT: 'node {}',
        }.get(self.language).format(prog_path)

        try:
            logger.info('EXECUTING ' + str(self.__save_path))
            subprocess.run(execute_command.split(), check=False)
        except:
            logger.opt(exception=True).error(f"Failed to execute {self.__save_path}")
            raise exc.CantRunProgram()
from io import StringIO
import flet as ft
from .frontend.settings import COLORS

class OutputHandler(StringIO):
    '''Catches the standart output (stdout/stderr) and saves it to the flet element'''

    def __init__(self, element: ft.ListView, page: ft.Page):

        self.__element = element
        self.__page = page
        super().__init__()

    def write(self, text: str):
        super().write(text)

        self.__element.controls.append(ft.Text(text, color=COLORS["pastel_terminal_text"]))
        self.__page.update()

    def fileno(self):
        return None
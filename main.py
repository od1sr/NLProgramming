import flet as ft

from src.executor import Executor
from src.config import Language
from src import exceptions
import uuid
from threading import Thread
from time import sleep
from random import uniform
import os, sys
wait_timer = 0

COLORS = {
    "background": "#F0F4F8",
    "surface": "#FFFFFF",
    "primary": "#89C2D9",
    "secondary": "#FFA69E",
    "text": "#2B2D42",
    "text_muted": "#8D99AE",
    "accent": "#C7D6E1",
    "highlight": "#E2C044",
    "pastel_red": "#FFB5B5",
    "pastel_dark": "#4A5568"
}


def wait_timer_start(page: ft.Page, input_button: ft.IconButton, timer_text):
    global wait_timer
    wait_timer = 10
    input_button.disabled = True
    input_button.bgcolor = COLORS['accent']
    timer_text.visible = True
    page.update()

    while wait_timer > 0:
        sleep(1)
        wait_timer -= 1
        timer_text.value = f'{wait_timer}s'
        page.update()

    input_button.disabled = False
    input_button.bgcolor = COLORS["primary"]
    timer_text.value = ''
    timer_text.visible = False
    page.update()
        


def main(page: ft.Page):
    

    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Текстовый чат"
    page.window.icon = ft.Icons.BUILD_CIRCLE_OUTLINED
    page.bgcolor = COLORS["background"]
    page.padding = 20
    page.window_width = 800
    page.window_height = 600


    messages_column = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    carts:dict[str, Executor] = {}

    no_cards_text = ft.Container(
        content=ft.Column([ft.Text(
            "Пусто",
            size=16,
            color=COLORS["text_muted"],
        )], alignment=ft.alignment.center),
        alignment=ft.alignment.center
    )

    messages_column.controls.append(no_cards_text)

    timer_text = ft.TextField(
        '',
        
        color=ft.Colors.WHITE,
        text_size=12,
        width=40,
        height=20,
        text_align=ft.TextAlign('right'),
        border_width=0,
        content_padding=3,
        fill_color=COLORS["accent"],
        border_radius=15,
        offset=(-0.9, 0.7),
        
    )
    timer_text.disabled = True
    timer_text.visible = False


    language_select_drop_box = ft.Dropdown(
        'Язык', options=[ft.dropdown.Option('Python'), ft.dropdown.Option('C++'), ft.dropdown.Option('JavaScript')], 
        width=120,
        border_radius=15,
        border_width=0,
    )
    language_select_drop_box.value = 'Python'

    


    def create_message_card(input_text, mc, lang_drop_down):

        input_text.disabled = True
        
        # Remove "no cards" text if it exists
        try:
            if mc[0] and mc[0].content.controls[0].value == 'Пусто':
                mc.pop(0)
        except: ...
            
        
        # ! CODE CONTENT BLOCK =========================================
        code_content = ft.TextField(
            'Генерация...',
            color=COLORS["text"],
            text_size=14,
            multiline=True
        )
        code_content.disabled = True

        # ! LIBS CONTENT BLOCK ==========================================
        libs_content = ft.TextField(
            label='Необходимые библиотеки:',
            value='',
            color=COLORS["text"],
            text_size=14,
            multiline=True,
        )
        libs_content.disabled = True
        libs_content.visible = False
        
        # ! SELECTED LANGUAGE TEXT =======================================
        language_text = ft.Text(
            lang_drop_down.value,
            size=14,
            style=ft.TextStyle(color=COLORS["text_muted"]),
            selectable=True,
            text_align=ft.TextAlign.RIGHT,
            tooltip='Язык используемый на карточке - ' + lang_drop_down.value,
        )

        # ! WARNING MESSAGE OBJ ===========================================
        warning = ft.Text(
            'Ошибка',
            color=COLORS["pastel_red"],
            size=14,
            selectable=True,
        )
        warning_obj = ft.Icon(ft.Icons.WARNING_AMBER, color = COLORS["pastel_red"])
        warning.visible = False
        warning_obj.visible = False

        # ! YOU PROMT BLOCK ================================================
        you_text = ft.TextField(
            input_text.value,
            color=COLORS["text_muted"],
            text_size=14,
            multiline=True,
            border_width=0
        )
        you_text.disabled = True

        # ! BUILDING TEXT ===================================================
        building_text = ft.Text(
            '',
            color=COLORS["text_muted"],
            size=14,
            selectable=True,
        )
        building_text.visible = False
        

        # this cart id
        cart_id = str(uuid.uuid4())

        # ! FUNCTION FOR BUILDING CODE ======================================
        # ? (1) selected build path
        # ? (2) selected language
        # ? (3) for `python` selected libs
        # ? (4)  |-> install libs
        # ? (5)  |-> build code to .exe or run .py gile
        # ! =================================================================
        def build_code(e):
            if e is not None and e.path:
                building_text.visible = True
                selected_path = e.path
                # Here you can add code to save/build your file at the selected path
                building_text.value += 'Путь сохранения: ' + selected_path + '\n\n'
                page.update()
                # ! INSTALLING LIBS ==============================================
                if carts[cart_id].language == Language.PYTHON:
                    if carts[cart_id].dependecies:
                        for lib in carts[cart_id].dependecies:
                            building_text.value += 'Выполнение команды: ' + lib + '...\n'
                            page.update()
                            try:
                                os.system(lib)
                                building_text.value += '[ Успешно ]\n\n'
                                page.update()
                            except:
                                building_text.value += '[ Ошибка ]\n'
                                warning.value = 'Ошибка при установке библиотеки: ' + lib
                                warning.visible = True
                                warning_obj.visible = True
                                page.update()
                                return
                        
                # ! ==============================================================

                # ! BUILDING CODE ================================================
                carts[cart_id].save_code(selected_path)
                building_text.value += 'Код сохранён в: ' + selected_path + '\n'
                python_build_button.disabled = False
                page.update()

                
                if carts[cart_id].language == Language.CPP:
                    building_text.value += '\n'
                    building_text.value += 'Компиляция кода...\n'
                    page.update()
                    try:
                        carts[cart_id].build_program()
                        building_text.value += '[ Успешно ]'
                    except:
                        building_text.value += '[ Ошибка ]'

                
                run_button.disabled = False
                page.update()
                # ! ==============================================================

        text = input_text.value
        input_text.value = ""
        page.update()
        carts[cart_id] = Executor(text, Language(lang_drop_down.value))

        # ! FUCNTION FOR RUN CODE ================================================
        def run_code(e):
            selected_path = carts[cart_id].path
            if sys.platform == "win32":
                if carts[cart_id].language == Language.PYTHON:
                    os.system(f'start cmd /k python "{selected_path}"')
                elif carts[cart_id].language == Language.CPP:
                    print(selected_path)
                    os.system(f'start cmd /k "{str(selected_path).split('.')[0]}.exe"')



        def build_python_for_pyinstaller(e):
            select_path = carts[cart_id].path
            output_dir = os.path.dirname(select_path)
            building_text.value += 'Сборка с помощью pyinstaller...\n'
            page.update()
            building_text.value += f'Выполнение команды: pyinstaller --onefile "{select_path}" --distpath "{output_dir}"...\n'
            try:
                os.system(f'pyinstaller --onefile "{select_path}" --distpath "{output_dir}"')
                building_text.value += '[ Успешно ]\n'
                building_text.value += f'Исполняемый файл сохранен в: {output_dir}\n'
            except:
                building_text.value += '[ Ошибка ]\n'
                warning.value = 'Ошибка при сборке с помощью pyinstaller'
                warning.visible = True
                warning_obj.visible = True
            page.update()                
        # ! SAVE PATH PICKER ===============================================
        save_path_picker = ft.FilePicker(
            on_result=build_code
        )
        page.overlay.append(save_path_picker)
        page.update()


        # ! CODE RUN BUTTON ================================================
        run_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            on_click=run_code,
            tooltip="""
Запускает ранее собраный код или `.py` файл.

`Python` файлы возможно запустить без сборки, 
при этом будут предварительно установленны необходимые зависимости в глобаальную область.
"""
        )
        run_button.visible = False
        run_button.disabled = True

        # ! PYTHON BUILD BUTTON =============================================
        python_build_button = ft.TextButton(
            'Использовать pyinstaller',
            icon=ft.icons.BUILD_CIRCLE,
            on_click=build_python_for_pyinstaller,
            tooltip="""
СБорка `Python` кода с использованием `pyinstaller`.
Для сборки необходимо указать путь к файлу, в который будет сохранен результат сборки.
"""
        )
        python_build_button.disabled = True
        python_build_button.visible = False

        # ! BUILD BUTTON ====================================================
        build_button = ft.TextButton(
            "Сoбрать" if carts[cart_id].language == Language.CPP else "Сохранить",
            icon=ft.icons.BUILD_CIRCLE if carts[cart_id].language == Language.CPP else ft.icons.SAVE,
            on_click=lambda _: save_path_picker.get_directory_path(),
            tooltip="""
Собирает икод в испольняемый .exe файл.
Для сборки необходимо указать путь к файлу, в который будет сохранен результат сборки.

Для сборки `C++` кода будет использоваться компилятор `g++`.
""" if carts[cart_id].language == Language.CPP else """
Сохраняет код в файл.
Для сохранения необходимо указать путь к файлу, в который будет сохранен результат сборки.
"""
        )
        build_button.visible = False

        
        # ! CART CONTAINER ================================================
        cntr = ft.Container(
            content=ft.Column([
                # ? UP LANGUAGE TEXT ======================================
                ft.Row([language_text], alignment=ft.MainAxisAlignment.END),
                

                # ? YOU PROMT BLOCK =======================================
                ft.Divider(height=1, color=COLORS["accent"]),
                you_text,
                ft.Divider(height=1, color=COLORS["accent"]),

                # ? CODE CONTENT BLOCK ====================================
                code_content,

                # ? LIBS CONTENT BLOCK ====================================
                libs_content,
                #ft.Divider(height=1, color=COLORS["accent"]),

                

                
                ft.Row([
                    # ? RUN BUTTON ========================================
                    run_button,

                    # ? BUILD BUTTON ======================================
                    build_button,
                    python_build_button,

                    # ? WARNING MESSAGE ===================================
                    warning_obj,
                    warning,
                ], spacing=5),

                building_text
            ], spacing=8),

            padding=15,
            margin=ft.margin.only(bottom=10),
            bgcolor=COLORS["surface"],
            border_radius=10,
            border=ft.border.all(1, COLORS["accent"]),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.BLACK12),
        )
        mc.append(
            cntr
        )

        

        
        
        error_handled = False
        Thread(target=wait_timer_start, args=[page, send_button, timer_text] ).start()
        try:
            carts[cart_id].generate()
            code_content.value = ''
            code_strokes = carts[cart_id].code.split('\n')
            for i in range(len(code_strokes)):
                code_content.value += code_strokes[i] + '\n'
                messages_column.scroll_to(offset=messages_column.height, duration=30)
                sleep(uniform(0, 0.2))
                page.update()
            
            if carts[cart_id].language == Language.PYTHON:
                python_build_button.visible = True
                if len(carts[cart_id].dependecies) > 0:
                    libs_content.value = '\n'.join(carts[cart_id].dependecies)
                    libs_content.visible = True
                    page.update()

            run_button.visible = True
            build_button.visible = True

        except exceptions.CantExtractCode:
            warning.value = "Не удалось получить данные кода."
            error_handled = True
            warning_obj.tooltip = """
Не получилось извлеч код из ответа. Это может возникнть из-за некорректного ответа от сервера. Или из-за некорректного запроса.
Это не языковая модель, а инструмент для генерации кода поэтому не пытайтесь с ней общаться!
"""
        except exceptions.ToManyRequests:
            error_handled = True
            warning.value = "Слишком много запросов подряд. Подождите немного и повторите попытку."
            warning_obj.tooltip = """
При отправке запроса на генерацию кода, не старайтесь отправлять запросы слишком часто.
Иначе интервал запросов будет возрастать, что приведет к ошибке и блокировке всех последующих запросов на генерацию кода на неопределенное время.
"""

        if error_handled:
            warning_obj.visible = True
            warning.visible = True
            code_content.value = ""
            code_content.visible = False
        
        input_text.disabled = False
        
        
        
        
        

    def send_message(e):
        if input_text.value.strip():
            create_message_card(input_text, messages_column.controls, language_select_drop_box)
            
            page.update()

    input_text = ft.TextField(
        hint_text="Введите запрос...",
        border_color=COLORS["accent"],
        cursor_color=COLORS["primary"],
        text_style=ft.TextStyle(color=COLORS["text"], size=14),
        multiline=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        fill_color=COLORS["surface"],
        border_radius=12,
        border_width=1.2,
        on_submit=send_message,
        width=600
    )

    send_button = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        icon_color=COLORS["surface"],
        bgcolor=COLORS["primary"],
        tooltip="Отправить",
        on_click=send_message,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=12,
        )
    )

    page.add(
        ft.Column([
            ft.Container(
                content=messages_column,
                expand=True,
                border_radius=15,
                bgcolor=COLORS["surface"],
                border=ft.border.all(1.2, COLORS["accent"]),
                padding=15,
                shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.BLACK12)
            ),
            ft.Container(
                content=ft.Row(
                    [language_select_drop_box,input_text, send_button, timer_text],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=ft.colors.TRANSPARENT,
                border=ft.border.all(0, ft.colors.TRANSPARENT),
                shadow=None,
                padding=0
            )
        ], 
        expand=True, 
        spacing=20)
    )
ft.app(target=main)
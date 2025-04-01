from src.executor import Executor
from src.config import Language
from threading import Thread
from random import uniform
from src import exceptions
from time import sleep
import flet as ft
from src.outputHandler import OutputHandler
import os, sys
import uuid
from loguru import logger

from src.frontend.ui_elements import *
from src.frontend.settings import REMOTE_SERVER

import socket


INTERNET_CONECTED = False
def is_connected(hostname):
    try:
        # See if we can resolve the host name - tells us if there is
        # A DNS listening
        host = socket.gethostbyname(hostname)
        # Connect to the host - tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except Exception:
        pass # We ignore any errors, returning False
    return False



wait_timer = 0
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

generate_flag = False
generate_errored = False

def start_generate_timer(page: ft.Page, timer_text):
    global generate_timer
    generate_timer = 0
    timer_text.value = f'{generate_timer}s'
    page.update()
    while not generate_flag:
        sleep(1)
        generate_timer += 1
        timer_text.value = f'{generate_timer}s'
        page.update()
    timer_text.value = f'Время ожидания: {generate_timer}s'
    timer_text.color = COLORS["text_muted"]
    if generate_errored:
        timer_text.color = COLORS["pastel_red"]
    page.update()

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Текстовый чат"
    page.window.icon = ft.Icons.BUILD_CIRCLE_OUTLINED
    page.bgcolor = COLORS["background"]
    page.padding = 20
    page.window_width = 800
    page.window_height = 600

    IS_CONSOLE_VISIBLE = False


    carts: dict[str, Executor] = {}

    messages_column.controls.append(no_cards_text)

    
    def create_message_card(input_text, mc, lang_drop_down):
        global generate_flag, generate_errored

        input_text.disabled = True
        
        try:
            if mc[0] and mc[0].content.controls[0].value == 'Пусто':
                mc.pop(0)
        except: pass

        

        
        
        language_text = ft.Text(
            lang_drop_down.value,
            size=14,
            style=ft.TextStyle(color=COLORS["text_muted"]),
            selectable=True,
            text_align=ft.TextAlign.RIGHT,
            tooltip='Язык используемый на карточке - ' + lang_drop_down.value,
        )

        warning = ft.Text(
            'Ошибка',
            color=COLORS["pastel_red"],
            size=14,
            selectable=True,
        )
        warning_obj = ft.Icon(ft.Icons.WARNING_AMBER, color=COLORS["pastel_red"])
        warning.visible = False
        warning_obj.visible = False

        you_text = ft.TextField(
            input_text.value,
            color=COLORS["text_muted"],
            text_size=14,
            multiline=True,
            border_width=0
        )
        you_text.disabled = True

        building_text = ft.Text(
            '',
            color=COLORS["text_muted"],
            size=14,
            selectable=True,
        )
        building_text.visible = False

        waiting_animation = ft.ProgressRing(width=18, height=18, stroke_width=3, color=COLORS["primary"])
        waiting_animation.visible = False

        generate_text = ft.Text(
            'Генерация',
            size=14,
            style=ft.TextStyle(color=COLORS["primary"]),
        )
        generate_text.visible = False  

        generate_timer_text = ft.Text(
            '0s',
            size=14,
            style=ft.TextStyle(color=COLORS["primary"]),
        )

        def delete_card(e):
            messages_column.controls.remove(cntr)
            del carts[cart_id]
            if not messages_column.controls:
                messages_column.controls.append(no_cards_text)
            page.update()

        delete_button = ft.IconButton(
            icon=ft.icons.DELETE_FOREVER_ROUNDED,
            icon_color=COLORS["pastel_red"],
            tooltip="Удалить карточку",
            on_click=delete_card,
            icon_size=20
        )

        cart_id = str(uuid.uuid4())

        def build_code(e):
            if e is not None and e.path:
                building_text.visible = True
                selected_path = e.path
                building_text.value += 'Путь сохранения: ' + selected_path + '\n\n'
                page.update()

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

                carts[cart_id].save_code(selected_path)
                building_text.value += 'Код сохранён в: ' + selected_path + '\n'
                python_build_button.disabled = False
                page.update()

                if carts[cart_id].language == Language.CPP:
                    building_text.value += '\nКомпиляция кода...\n'
                    page.update()
                    try:
                        carts[cart_id].build_program()
                        building_text.value += '[ Успешно ]'
                    except:
                        building_text.value += '[ Ошибка ]'

                run_button.disabled = False
                page.update()

        text = input_text.value
        input_text.value = ""
        page.update()
        carts[cart_id] = Executor(text, Language(lang_drop_down.value))

        def run_code(e):
            selected_path = carts[cart_id].path
            if sys.platform == "win32":
                if carts[cart_id].language == Language.PYTHON:
                    os.system(f'start cmd /k python "{selected_path}"')
                elif carts[cart_id].language == Language.CPP:
                    os.system(f'start cmd /k "{str(selected_path).split(".")[0]}.exe"')

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

        save_path_picker = ft.FilePicker(on_result=build_code)
        page.overlay.append(save_path_picker)
        page.update()

        run_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            on_click=run_code,
            tooltip="Запускает ранее собранный код",
            visible=False,
            disabled=True
        )

        python_build_button = ft.TextButton(
            'Использовать pyinstaller',
            icon=ft.icons.BUILD_CIRCLE,
            on_click=build_python_for_pyinstaller,
            tooltip="Сборка Python кода с pyinstaller",
            disabled=True,
            visible=False
        )

        build_button = ft.TextButton(
            "Собрать" if carts[cart_id].language == Language.CPP else "Сохранить",
            icon=ft.icons.BUILD_CIRCLE if carts[cart_id].language == Language.CPP else ft.icons.SAVE,
            on_click=lambda _: save_path_picker.get_directory_path(),
            visible=False
        )


        


       

        cntr = ft.Container(
            content=ft.Column([
                ft.Row([delete_button, ft.Container(expand=True), language_text],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=COLORS["accent"]),
                you_text,
                ft.Divider(height=1, color=COLORS["accent"]),
                code_content,
                libs_content,
                ft.Row([
                    run_button,
                    build_button,
                    python_build_button,
                    warning_obj,
                    warning,
                    waiting_animation,
                    generate_text,
                    ft.Container(expand=True),
                    generate_timer_text
                ], spacing=9, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                building_text
            ], spacing=8),
            padding=15,
            margin=ft.margin.only(bottom=10),
            bgcolor=COLORS["surface"],
            border_radius=10,
            border=ft.border.all(1, COLORS["accent"]),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.BLACK12),
        )
        mc.append(cntr)

        error_handled = False
        generate_flag = False
        generate_errored = False
        Thread(target=wait_timer_start, args=[page, send_button, timer_text]).start()
        Thread(target=start_generate_timer, args=[page, generate_timer_text]).start()

        try:
            waiting_animation.visible = True
            generate_text.visible = True
            delete_button.disabled = True
            delete_button.icon_color = COLORS["text_muted"]
            page.update()
            carts[cart_id].generate()
            delete_button.icon_color = COLORS["pastel_red"]
            delete_button.disabled = False
            generate_flag = True
            waiting_animation.visible = False
            generate_text.visible = False
            code_content.visible = True
            code_content.value = ''
            code_strokes = carts[cart_id].code.split('\n')
            for i in range(len(code_strokes)):
                sleep(uniform(0, 0.05))
                code_content.value += code_strokes[i] + '\n'
                #md.value += code_strokes[i] + '\n'
                page.update()
                messages_column.scroll_to(offset=messages_column.height, duration=3)

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
        except exceptions.ToManyRequests:
            error_handled = True
            warning.value = "Слишком много запросов подряд."
        except exceptions.NetworkError:
            error_handled = True
            warning.value = "Отсуствует подключение к сети."
        except exceptions.CantGetResponseFromAI:
            error_handled = True
            warning.value = "Не удалось получить данный с серврера."

        if error_handled:
            warning_obj.visible = True
            warning.visible = True
            code_content.value = ""
            code_content.visible = False
            generate_errored = True
            generate_flag = True
            waiting_animation.visible = False
            generate_text.visible = False
            delete_button.icon_color = COLORS["pastel_red"]
            delete_button.disabled = False
        
        input_text.disabled = False

    def send_message(e):
        if input_text.value.strip():
            create_message_card(input_text, messages_column.controls, language_select_drop_box)
            page.update()

    internet_connection = ft.IconButton(
        icon=ft.Icons.SIGNAL_WIFI_CONNECTED_NO_INTERNET_4
    )
    internet_connection.disable = True

    def check_internet_connection(page, internet_c):
        global INTERNET_CONECTED
        while True:
            sleep(2)
            INTERNET_CONECTED = is_connected(REMOTE_SERVER)
            if not INTERNET_CONECTED:
                internet_c.icon = ft.Icons.SIGNAL_WIFI_CONNECTED_NO_INTERNET_4
                internet_c.tooltype = "Не в сети"
            else:
                internet_c.icon = ft.Icons.SIGNAL_WIFI_4_BAR
                internet_c.tooltype = "В сети"
            page.update()
            


    Thread(target=check_internet_connection, args=[page, internet_connection]).start()

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

    console = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    console.controls.append(ft.Text('Консоль', color=COLORS["pastel_terminal_text"]))

    out = OutputHandler(console, page)
    logger.add(out)
    logger.info('Console configured!!!')
    

    console_container = ft.Container(
        content=console,
        expand=True,
        border_radius=15,
        border=ft.border.all(1.2, COLORS["accent"]),
        bgcolor=COLORS["pastel_terminal"],
        shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.BLACK12),
        padding=15,
        offset=ft.transform.Offset(0, 0),
        animate_offset=ft.Animation(200, "easeOutQuad"),
        right=20,
        top=20,
        bottom=20,
        width=600,
        
    )

    console_toggle_button = ft.IconButton(
        icon=ft.icons.CHEVRON_RIGHT,
        icon_color=COLORS["pastel_terminal_text"],
        bgcolor=COLORS["pastel_terminal"],
        on_click=lambda e: toggle_console(e),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        top=0,
        right=0,
        visible=True,
        tooltip="Скрыть/Показать консоль"
    )

    def toggle_console(e):
        nonlocal IS_CONSOLE_VISIBLE
        IS_CONSOLE_VISIBLE = not IS_CONSOLE_VISIBLE
        
        if IS_CONSOLE_VISIBLE:
            console_container.offset = ft.transform.Offset(0, 0)
            console_toggle_button.icon = ft.icons.CHEVRON_RIGHT
        else:
            console_container.offset = ft.transform.Offset(1.1, 0)
            console_toggle_button.icon = ft.icons.CHEVRON_LEFT
        
        page.update()

    def open_console():
        nonlocal IS_CONSOLE_VISIBLE
        IS_CONSOLE_VISIBLE = True
        
        if IS_CONSOLE_VISIBLE:
            console_container.offset = ft.transform.Offset(0, 0)
            console_toggle_button.icon = ft.icons.CHEVRON_RIGHT
        else:
            console_container.offset = ft.transform.Offset(1.1, 0)
            console_toggle_button.icon = ft.icons.CHEVRON_LEFT
        
        page.update()

    def close_console():
        nonlocal IS_CONSOLE_VISIBLE
        IS_CONSOLE_VISIBLE = False
        
        if IS_CONSOLE_VISIBLE:
            console_container.offset = ft.transform.Offset(0, 0)
            console_toggle_button.icon = ft.icons.CHEVRON_RIGHT
        else:
            console_container.offset = ft.transform.Offset(1.1, 0)
            console_toggle_button.icon = ft.icons.CHEVRON_LEFT
        
        page.update()

    page.add(
        ft.Stack(
            [
                ft.Column([
                    internet_connection,
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
                            [language_select_drop_box, input_text, send_button, timer_text],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=10
                    )
                ], expand=True),
                console_container,
                console_toggle_button
            ],
            expand=True
        )
    )
    close_console()

ft.app(target=main)
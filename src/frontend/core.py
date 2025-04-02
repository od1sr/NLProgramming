

from src.frontend.highlighter import highlight_python_code
from src.frontend.settings import REMOTE_SERVER
from src.frontend.scripts import *
from src.outputHandler import OutputHandler
from src.frontend.ui_elements import *
from src.executor import Executor
from src.config import Language
from threading import Thread
from random import uniform
from src import exceptions
from loguru import logger
from time import sleep
import flet as ft
import subprocess
import os, sys

import uuid




generate_flag = False
generate_errored = False
def start_generate_timer(page: ft.Page, timer_text):
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
    if generate_errored:  timer_text.color = COLORS["pastel_red"]
    page.update()

'''
    Main function
'''
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

        # Conent box for code
        code_content = ft.Text(
            size=14
        )
        
        # Content box for libs
        libs_content = ft.TextField(
            label='Необходимые библиотеки:',
            value='',
            color=COLORS["text"],
            text_size=14,
            multiline=True,
        )
        libs_content.disabled = True
        libs_content.visible = False

        
        
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
            # Анимация свайпа вправо
            cntr.animate_offset = ft.animation.Animation(300, ft.animation.AnimationCurve.EASE_OUT)
            cntr.offset = ft.transform.Offset(1.5, 0)  # Сдвигаем карточку вправо за пределы экрана
            
            # Обновляем страницу чтобы увидеть анимацию
            page.update()
            
            # Ждем завершения анимации перед удалением
            def delayed_remove():
                sleep(0.3)  # Ждем завершения анимации
                messages_column.controls.remove(cntr)
                del carts[cart_id]
                if not messages_column.controls:
                    messages_column.controls.append(no_cards_text)
                page.update()
            
            # Запускаем удаление в отдельном потоке
            Thread(target=delayed_remove).start()

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
                        commands = carts[cart_id].install_dependecies()

                        for lib_install_command in commands:
                            building_text.value += 'Выполнение команды: ' + lib_install_command + '...\n'
                            
                            page.update()

                            if commands.__next__(): # status
                                building_text.value += '[ Успешно ]\n\n'
                            else:
                                building_text.value += '[ Ошибка ]\n'
                                warning.value = 'Ошибка при установке библиотеки: ' + lib_install_command
                                warning.visible = True
                                warning_obj.visible = True

                            page.update()

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


        code_container = ft.Container(code_content, bgcolor=COLORS["code_background_light"], expand=True, border_radius=10, border=ft.border.all(1, COLORS["accent"]), padding=10)
        code_container.visible = False

       

        cntr = ft.Container(
            content=ft.Column([
                ft.Row([delete_button, ft.Container(expand=True), language_text],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=COLORS["accent"]),
                you_text,
                ft.Divider(height=1, color=COLORS["accent"]),
                code_container,
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
            offset=ft.transform.Offset(0, 0),  # Добавляем начальное положение
            animate_offset=ft.animation.Animation(300, ft.animation.AnimationCurve.ELASTIC_IN),  # Добавляем анимацию
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
            spans = highlight_python_code(carts[cart_id].code)
            code_container.visible = True
            for i in range(len(spans)):
                code_content.spans.append(spans[i])
                
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
            open_console()
        
        input_text.disabled = False

    def send_message(e):
        if input_text.value.strip():
            create_message_card(input_text, messages_column.controls, language_select_drop_box)
            page.update()

    internet_connection = ft.IconButton(
        icon=ft.Icons.SIGNAL_WIFI_CONNECTED_NO_INTERNET_4,
        
        bgcolor=COLORS["pastel_red"],
        icon_color=COLORS["vivid_red"],
        tooltip="Статус подключения к интернету",
        scale=0.8,

    )    
    internet_connection.disable = True


    def check_internet_connection(page, internet_c):

        while True:
            sleep(2)
            INTERNET_CONECTED = is_connected(REMOTE_SERVER)
            if not INTERNET_CONECTED:
                internet_c.icon = ft.Icons.SIGNAL_WIFI_CONNECTED_NO_INTERNET_4
                internet_c.tooltip = "Не в сети"
                internet_c.icon_color = COLORS["vivid_red"]
                internet_c.bgcolor = COLORS["pastel_red"]
                
            else:
                internet_c.icon = ft.Icons.SIGNAL_WIFI_4_BAR
                internet_c.tooltip = "В сети"
                internet_c.icon_color = COLORS["vivid_green"]
                internet_c.bgcolor = COLORS['pastel_green']
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

    out = OutputHandler(console, page)
    sys.stdout = sys.stderr = out
    logger.add(out)
    Executor.setDefaultOutStream(out)
    logger.info('Console inited.')

    def close_console():
        nonlocal IS_CONSOLE_VISIBLE
        IS_CONSOLE_VISIBLE = False
        
        if IS_CONSOLE_VISIBLE:
            console_container.offset = ft.transform.Offset(0, 0)
            console_toggle_button.icon = ft.Icons.CHEVRON_LEFT
        else:
            console_container.offset = ft.transform.Offset(1.1, 0)
            console_toggle_button.icon = ft.Icons.CHEVRON_RIGHT
        
        page.update()

    def open_console():
        nonlocal IS_CONSOLE_VISIBLE
        IS_CONSOLE_VISIBLE = True

        if IS_CONSOLE_VISIBLE:
            console_container.offset = ft.transform.Offset(0, 0)
            console_open_button.offset = ft.transform.Offset(1.5, 0)
            console_toggle_button.icon = ft.Icons.CHEVRON_RIGHT
        else:
            console_container.offset = ft.transform.Offset(1.1, 0)
            console_open_button.offset = ft.transform.Offset(0, 0)
            console_toggle_button.icon = ft.Icons.CHEVRON_LEFT

        page.update()


    resize_handle = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.RESIZE_COLUMN,
        drag_interval=10,
        on_pan_update=lambda e: handle_resize(e),
        content=ft.Container(
            width=10,
            height=30,
            bgcolor=ft.Colors.with_opacity(0.5, COLORS["pastel_terminal_text"]),
            border_radius=5,
        ),
    )

    def toggle_console(e):
        nonlocal IS_CONSOLE_VISIBLE
        IS_CONSOLE_VISIBLE = not IS_CONSOLE_VISIBLE
        
        if IS_CONSOLE_VISIBLE:
            console_container.offset = ft.transform.Offset(0, 0)
            console_open_button.offset = ft.transform.Offset(1.5, 0)
            console_toggle_button.icon = ft.Icons.CHEVRON_RIGHT
        else:
            console_container.offset = ft.transform.Offset(1.1, 0)
            console_open_button.offset = ft.transform.Offset(0, 0)
            console_toggle_button.icon = ft.Icons.CHEVRON_LEFT
        
        page.update()

    console_toggle_button = ft.IconButton(
        icon=ft.Icons.CHEVRON_LEFT,
        icon_color=COLORS["pastel_terminal_text"],
        bgcolor=COLORS["pastel_terminal"],
        on_click=toggle_console,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        tooltip="Скрыть/Показать консоль"
    )

    console_open_button = ft.TextButton(
        "Логи",
        on_click=toggle_console,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=COLORS["pastel_terminal"],
            padding=12,
            color=ft.colors.WHITE,
        ),
        icon=ft.Icons.TERMINAL,
        icon_color=COLORS["pastel_terminal_text"],
        tooltip="Скрыть/Показать консоль",
        animate_offset=ft.Animation(200, "easeOutQuad"),
        offset=ft.transform.Offset(0, 0),
    )    

    console_container = ft.Container(
        content=ft.Column([
            ft.Row([
                resize_handle,
                ft.Text("Логи", color=ft.Colors.WHITE, offset=[0.5, 0], size=18),
                ft.Container(expand=True),
                console_toggle_button,
            ], spacing=0),
            console
        ]),
        width=400,  # Начальная ширина
        expand=True,
        border_radius=15,
        border=ft.border.all(1.2, COLORS["accent"]),
        bgcolor=ft.Colors.with_opacity(0.85, COLORS["pastel_terminal"]),
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK12),
        padding=15,
        offset=ft.transform.Offset(0, 0),
        animate_offset=ft.Animation(200, "easeOutQuad"),
        right=0,
        top=1,
        bottom=1,
    )

    

    


    

    def handle_resize(e):
        # Минимальная и максимальная ширина консоли
        min_width = 300
        max_width = page.window_width - 100
        
        # Вычисляем новую ширину
        new_width = console_container.width - e.delta_x
        new_width = max(min_width, min(new_width, max_width))
        
        console_container.width = new_width
        page.update()

    page.add(
        ft.Stack(
            [
                ft.Column([
                    ft.Row([
                        internet_connection, 
                        ft.Container(expand=True),
                        console_open_button
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        content=messages_column,
                        expand=True,
                        border_radius=15,
                        bgcolor=COLORS["surface"],
                        border=ft.border.all(1.2, COLORS["accent"]),
                        padding=15,
                        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK12)
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
                
            ],
            expand=True
        )
    )
    close_console()


def start():
    """
    Запускает основное приложение с графическим интерфейсом.
    
    Эта функция инициализирует и запускает основное приложение, используя фреймворк Flet (ft).
    Она передает функцию main в качестве целевой функции в ft.app().
    
    Функция main содержит всю логику приложения, включая:
    - Настройку внешнего вида окна (размер, цвет, иконка)
    - Инициализацию всех UI элементов (кнопки, текстовые поля, выпадающие списки)
    - Обработку пользовательского ввода
    - Управление консолью вывода
    - Создание и управление карточками с кодом
    - Обработку генерации кода
    - Мониторинг интернет-соединения
    - Сборку и запуск сгенерированного кода
    
    Returns:
        None
    
    Raises:
        Любые исключения, которые могут возникнуть при инициализации или работе приложения
        будут обработаны внутри функции main
    """
    ft.app(target=main)
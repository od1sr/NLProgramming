import flet as ft
from src.frontend.settings import COLORS

# message column ==========================
messages_column = ft.ListView(expand=True, spacing=10, auto_scroll=True)


# Timer text ===============================
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


# No carts text =============================
no_cards_text = ft.Container(
    content=ft.Column([ft.Text(
        "Пусто",
        size=16,
        color=COLORS["text_muted"],
    )], alignment=ft.alignment.center),
    alignment=ft.alignment.center
)

# language selector
language_select_drop_box = ft.Dropdown(
    'Язык', 
    options=[
        ft.dropdown.Option('Python'),
        ft.dropdown.Option('C++'),
        ft.dropdown.Option('JavaScript')
    ], 
    width=120,
    border_radius=15,
    border_width=0,
)
language_select_drop_box.value = 'Python'

# UI FOR MESSAGE CART ========================================



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





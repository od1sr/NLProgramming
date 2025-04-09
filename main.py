import flet as ft
from src.frontend.settings import COLORS
from src.frontend.core import start
from time import sleep
import random

def show_loading_screen(page: ft.Page):
    page.window.center()
    page.window.width = 600
    page.window.height = 350
    page.window.resizable = False
    page.window.title_bar_hidden = True
    page.bgcolor = COLORS["background"]
    

    progress_bar = ft.ProgressBar(
        color=COLORS["text"],
        bgcolor=COLORS["text_muted"],
        height=2,
        value=0
    )
    
    loading_status = ft.Text(
        "Initializing...",
        size=12,
        color=COLORS["text_muted"],
    )
    
    # Container for progress bar at the bottom
    progress_container = ft.Container(
        content=ft.Column([
            loading_status,
            progress_bar
        ]),
        padding=ft.padding.only(bottom=0),
        alignment=ft.alignment.center
    )
    
    AppIcon = ft.Image(
        src="assets/logo.png",
        width=50,
        height=50,
        fit=ft.ImageFit.CONTAIN,
        border_radius=10,
    )

    title_row = ft.Row(
        controls=[
            ft.Text(
                "AI-Assist",
                size=34,
                color=COLORS["text"],
                weight=ft.FontWeight.BOLD
            ),
            AppIcon
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    By = ft.Text(
        "By Pavlov Ivan & Semenov Roman",
        size=14,
        color=COLORS["text_muted"],
        offset=(0, -0.3)
    )

    loading_texts = [
        "Initializing...",
        "Checking file pathes...",
        "Loading modules...",
        "Loading settings...",
        "Loading UI...",
        "Loading fonts...",
        "Loading icons...",
        "Loading colors...",
        "Preparing for launch...",
        "Launching...",
    ]


    content_column = ft.Column(
        controls=[
            title_row,
            By,
            ft.Container(
                padding=0,
                expand=True,
                alignment=ft.alignment.center
            ),
            progress_container
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True
    )
    

    main_container = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=content_column,
                    expand=True,
                    padding=0
                ),
                
            ],
            spacing=0,
            expand=True
        ),
        expand=True,
        border_radius=0,
    )
    
    page.add(main_container)
    page.update()
    

    progress = 0
    text_index = 0
    while progress < 10:
        progress += random.uniform(0.0001, 0.5)
        if progress > 10:
            progress = 10
        progress_bar.value = progress / 10
        
        text_index = min(int(progress), 9)
        loading_status.value = loading_texts[text_index]
        
        page.update()
        sleep(0.1)
    
    sleep(0.5)
    page.window.close()

ft.app(target=show_loading_screen)
start()
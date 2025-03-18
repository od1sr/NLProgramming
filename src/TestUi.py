import flet as ft

def main(page: ft.Page):
    page.title = "Flet Input/Output Example"
    page.window_maximized = True 
    page.bgcolor = ft.colors.GREY_100

    input_text = ft.TextField(label="Input", multiline=True, expand=True,bgcolor=ft.colors.BLUE_GREY_300)
    output_text = ft.TextField(
        multiline=True,
        expand=True,
        read_only=True,
        bgcolor=ft.colors.GREEN_100, 
        border=ft.InputBorder.NONE, 
    )

    def submit_clicked(e):
        output_text.value = input_text.value
        page.update()

    row = ft.Row(
        [
            ft.Column(
                [
                    input_text,
                    ft.Container(
                        content=ft.ElevatedButton("Submit", on_click=submit_clicked, expand=True, bgcolor = ft.colors.BLUE_GREY_100),
                        alignment=ft.alignment.center
                    ),
                ],
                expand=1,
            ),
            ft.Column(
                [
                    output_text,
                ],
                expand=1,
            ),
        ],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    page.add(row)


if __name__ == "__main__":
    ft.app(target=main)
import flet as ft
import re

def highlight_python_code(code):
    # Простые регулярные выражения для подсветки Python
    patterns = {
        'keyword': r'\b(and|as|assert|break|class|continue|def|del|elif|else|except|while|finally|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|self)\b',
        'string': r'(\'[^\']*\'|"[^"]*")',
        'comment': r'#[^\n]*',
        'number': r'\b\d+\b',
        'builtin': r'\b(print|len|range|str|int|float|list|dict|tuple|set|input)\b',
        'function_name': r'\b(?!if|for|while|elif\b)[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'    }
    
    spans = []
    text = code
    
    for name, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            spans.append({
                "from": match.start(),
                "to": match.end(),
                "name": name
            })
    
    # Сортируем спаны по позиции
    spans.sort(key=lambda x: x['from'])
    
    # Создаем TextSpans
    text_spans = []
    last_pos = 0
    
    for span in spans:
        if span['from'] > last_pos:
            text_spans.append(
                ft.TextSpan(text[last_pos:span['from']])
            )
        text_spans.append(
            ft.TextSpan(
                text[span['from']:span['to']],
                style=ft.TextStyle(color=get_color_for_span(span['name']))
        ))
        last_pos = span['to']
    
    if last_pos < len(text):
        text_spans.append(ft.TextSpan(text[last_pos:]))
    
    return text_spans

def get_color_for_span(name):
    colors = {
        'keyword': '#0066CC',    # primary
        'string': '#008000',     # vivid_green
        'comment': '#808080',    # text_muted
        'number': '#B8860B',     # highlight
        'builtin': '#8B0000',    # secondary
        "function_name": '#0000FF' # accent
    }
    return colors.get(name, '#FFFFFF')


if __name__ == "__main__":
    # using
    def main(page: ft.Page):
        code_field = ft.TextField(
            multiline=True,
            min_lines=20,
            expand=True,
            on_change=lambda e: update_highlight(e)
        )
        
        highlighted_text = ft.Text()
        
        def update_highlight(e):
            text_spans = highlight_python_code(code_field.value)
            print(text)
            highlighted_text.spans = text_spans
            highlighted_text.value = ""  # Очищаем value, так как используем spans
            highlighted_text.update()
        
        page.add(
            ft.Column([
                code_field,
                ft.Divider(),
                highlighted_text
            ])
        )

    ft.app(target=main)
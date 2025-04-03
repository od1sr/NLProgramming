import flet as ft
import re

def highlight_python_code(code):
    # Простые регулярные выражения для подсветки Python
    patterns = {
        'string': r'(\'[^\']*\'|"[^"]*")',
        'comment': r'#[^\n]*',
        'keyword': r'\b(and|as|assert|break|class|continue|def|for|del|elif|else|except|while|finally|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|with|yield|self)\b',
        'number': r'\b\d+\b',
        'builtin': r'\b(print|len|range|str|int|float|list|dict|tuple|set|input|abs|all|any|bin|bool|chr|complex|dir|divmod|enumerate|eval|exec|filter|format|frozenset|getattr|globals|hasattr|hash|hex|id|isinstance|issubclass|iter|locals|map|max|min|next|oct|open|ord|pow|property|reversed|round|slice|sorted|sum|super|type|vars|zip)\b',
        'function_name': r'\b(?!(?:and|as|assert|break|class|continue|def|for|del|elif|else|except|while|finally|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|with|yield|self|print|len|range|str|int|float|list|dict|tuple|set|input)\b)[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()',
        'constant': r'\b(True|False|None)\b'
    }
    
    spans = []
    text = code
    
    # Создаем список всех совпадений
    all_matches = []
    
    # Сначала находим строки и комментарии
    protected_regions = []
    for name in ['string', 'comment']:
        for match in re.finditer(patterns[name], text):
            protected_regions.append((match.start(), match.end()))
            all_matches.append({
                "from": match.start(),
                "to": match.end(),
                "name": name,
                "text": text[match.start():match.end()]
            })
    
    # Затем ищем остальные паттерны, исключая защищенные регионы
    for name, pattern in patterns.items():
        if name not in ['string', 'comment']:
            for match in re.finditer(pattern, text):
                # Проверяем, не находится ли совпадение в защищенном регионе
                is_protected = False
                for start, end in protected_regions:
                    if match.start() >= start and match.end() <= end:
                        is_protected = True
                        break
                if not is_protected:
                    all_matches.append({
                        "from": match.start(),
                        "to": match.end(),
                        "name": name,
                        "text": text[match.start():match.end()]
                    })
    
    # Сортируем по позиции
    all_matches.sort(key=lambda x: x['from'])
    
    # Удаляем перекрывающиеся совпадения, оставляя приоритетные
    filtered_matches = []
    for match in all_matches:
        overlapping = False
        for existing in filtered_matches:
            if (match['from'] >= existing['from'] and match['from'] < existing['to']) or \
               (match['to'] > existing['from'] and match['to'] <= existing['to']):
                overlapping = True
                break
        if not overlapping:
            filtered_matches.append(match)
    
    # Создаем TextSpans
    text_spans = []
    last_pos = 0
    
    for match in filtered_matches:
        if match['from'] > last_pos:
            text_spans.append(
                ft.TextSpan(text[last_pos:match['from']])
            )
        text_spans.append(
            ft.TextSpan(
                match['text'],
                style=ft.TextStyle(color=get_color_for_span(match['name']))
        ))
        last_pos = match['to']
    
    if last_pos < len(text):
        text_spans.append(ft.TextSpan(text[last_pos:]))
    
    return text_spans

def get_color_for_span(name):
    colors = {
        'keyword': '#6200EE',    # primary
        'string': '#00C853',     # green
        'comment': '#757575',    # gray
        'number': '#2962FF',     # blue
        'builtin': '#D50000',    # red
        'function_name': '#3700B3', # deep purple
        'constant': '#FF6D00'    # orange
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
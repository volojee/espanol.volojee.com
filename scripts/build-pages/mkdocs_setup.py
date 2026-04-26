# mkdocs_setup.py
import os, re, sys, yaml, unicodedata
from pathlib import Path

def slugify(text: str) -> str:
    cyr = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y',
        'к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f',
        'х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
        'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'Yo','Ж':'Zh','З':'Z','И':'I','Й':'Y',
        'К':'K','Л':'L','М':'M','Н':'N','О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F',
        'Х':'Kh','Ц':'Ts','Ч':'Ch','Ш':'Sh','Щ':'Shch','Ъ':'','Ы':'Y','Ь':'','Э':'E','Ю':'Yu','Я':'Ya'
    }
    out = [cyr.get(c, c) for c in text]
    text = ''.join(out)
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'page'

def preprocess_joplin(content: str) -> str:
    lines = content.split('\n')
    cleaned = []
    in_table = False

    for line in lines:
        # Определяем строки таблицы: начинаются с '|' или '> |'
        is_table_row = re.match(r'^\s*>?\s*\|', line) is not None

        if is_table_row:
            # Убираем маркер цитаты '> ' только у строк таблицы
            line = re.sub(r'^\s*>\s*', '', line)

            if not in_table:
                # Начало новой таблицы: гарантируем одну пустую строку перед ней
                if cleaned and cleaned[-1].strip() != '':
                    cleaned.append('')
                in_table = True
        else:
            in_table = False

        cleaned.append(line)

    return '\n'.join(cleaned)

def main():
    inp = Path('/data/input')
    # 📍 Используем /app (рабочая директория контейнера)
    docs = Path('docs')
    docs.mkdir(exist_ok=True, parents=True)

    pages = []
    slug_counts = {}

    for f in sorted(inp.glob('*.md')):
        content = f.read_text('utf-8')
        content = preprocess_joplin(content)

        raw_slug = slugify(f.stem)
        slug_counts[raw_slug] = slug_counts.get(raw_slug, -1) + 1
        slug = f"{raw_slug}-{slug_counts[raw_slug]}" if slug_counts[raw_slug] > 0 else raw_slug

        def fix_link(m):
            prefix, suffix = m.group(1), m.group(2) or ""
            target_stem = Path(prefix).stem
            new_slug = slugify(target_stem)
            return f']({new_slug}.md{suffix})'
        content = re.sub(r'\]\(([^)#\n]+?)\.md(#.*?)?\)', fix_link, content)

        (docs / f"{slug}.md").write_text(content, 'utf-8')

        title = next((l.strip()[2:] for l in content.splitlines() if l.strip().startswith('# ')), f.stem.replace('-',' ').title())
        pages.append({'slug': slug, 'title': title})

    idx_lines = [
        "# 📚 Уроки испанского",
        "",
        "> Здесь собраны конспекты занятий по испанскому языку.",
        "> <br>Материалы созданы с помощью ИИ и могут содержать ошибки.",
        "",
        "", "Выберите раздел:",
        "",
    ]

    idx_lines += [f"- [{p['title']}]({p['slug']}.md)" for p in pages]

    (docs / "index.md").write_text('\n'.join(idx_lines), 'utf-8')

    # 🔽 ПЛОСКОЕ МЕНЮ (убран уровень "Разделы")
    nav_struct = [{'Главная': 'index.md'}] + [{p['title']: f"{p['slug']}.md"} for p in pages]

    # 🔽 Генерация custom.css
    (docs / 'custom.css').write_text(
        ".md-typeset table:not(.highlighttable) {\n"
        "    font-size: 0.8rem;\n"
        "}\n"
        ".md-typeset table:not(.highlighttable) td,\n"
        ".md-typeset table:not(.highlighttable) th {\n"
        "    padding: 0.5em 1em;\n"
        "}\n", 'utf-8'
    )

    cfg = {
        'site_name': 'Уроки испанского',
        'docs_dir': 'docs',           # Относительно /app
        'site_dir': '/data/output',   # Примонтированная папка
        'use_directory_urls': False,
        'extra_css': ['custom.css'],
        'theme': {
            'name': 'material',
            'language': 'ru',  # 🔽 АВТОПЕРЕВОД ИНТЕРФЕЙСА (Содержание, Поиск и т.д.)
            #'font': False,  # 🔽 Отключаем Google Fonts (используются системные шрифты)
            'palette': [
                {'scheme': 'default', 'toggle': {'icon': 'material/weather-night', 'name': 'Тёмная тема'}},
                {'scheme': 'slate', 'toggle': {'icon': 'material/weather-sunny', 'name': 'Светлая тема'}}
            ],
            'features': [
                'navigation.instant', 'navigation.tracking', 'navigation.top',
                'search.highlight', 'search.suggest', 'content.code.copy', 'header.autohide'
            ]
        },
        'plugins': [
            {'search': {'enabled': True}},
            # {'privacy': {'enabled': True}},
            {'offline': {'enabled': True}}
        ],
        'markdown_extensions': [
            {'toc': {'permalink': '🔗', 'toc_depth': 4}},
            'tables', 'fenced_code', 'attr_list', 'def_list', 'footnotes',
            {'pymdownx.highlight': {'anchor_linenums': True, 'line_spans': '__span', 'pygments_lang_class': True}},
            'pymdownx.inlinehilite',
            'pymdownx.snippets',
            'pymdownx.superfences',
            'pymdownx.critic',
            'pymdownx.caret',
            'pymdownx.keys',
            'pymdownx.mark',
            'pymdownx.tilde',
            'pymdownx.details',
        ],
        'nav': nav_struct
    }
    # 📍 Записываем в /app/mkdocs.yml
    Path('mkdocs.yml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False, default_flow_style=False), 'utf-8')
    print("✅ Конфигурация готова. Запуск сборки...")

if __name__ == '__main__':
    main()

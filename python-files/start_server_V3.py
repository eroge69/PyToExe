import sys
import sqlite3
import nicegui
from nicegui import ui
print('python version: ' + sys.version)
print('nicegui version: ' + nicegui.__version__)
print('sqlite3 version: ' + sqlite3.sqlite_version)

select_comp=0
nameDB ='radio_components.db'
def newDB():
    # Подключение к базе данных
    conn = sqlite3.connect(nameDB)
    cursor = conn.cursor()
    # Создание таблицы, если она не существует
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS radio_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    value REAL NOT NULL,
    description TEXT )
    ''')
    conn.commit()
    conn.close()

def delDB():
    # Подключение к БД
    conn = sqlite3.connect(nameDB)
    cursor = conn.cursor()
    # Удаление таблицы
    cursor.execute('DROP TABLE IF EXISTS radio_components')
    # Сохранение изменений
    conn.commit()
    # Закрытие соединения
    conn.close()

def add_test():
    name_input.value = 'Р1-12-0,1-1 кОм±5%-М-«А»'
    value_input.value = '1 кОм'
    description_input.value = 'Резистор, 0,1Вт, 1%'
    add_component()
    name_input.value = '08055A120JAT'
    value_input.value = '12 пФ'
    description_input.value = 'Конденсатор, 50В, 5%'
    add_component()
    name_input.value = ''
    value_input.value = ''
    description_input.value = ''

# Функция для добавления радио компонента
def add_component():
    # Подключение к базе данных
    conn = sqlite3.connect(nameDB)
    cursor = conn.cursor()
    
    name = name_input.value
    value = value_input.value
    description = description_input.value
    try:
        cursor.execute('INSERT INTO radio_components (name, value, description) VALUES (?, ?, ?)',
                    (name, value, description))
        conn.commit()
        ui.notify('Радио компонент ' + name +' добавлен!')
    except sqlite3.IntegrityError:
        print(f"Имя '{name}' уже существует.")
        ui.notify(f"Имя '{name}' уже существует.!")
    finally:
        conn.close()
        name_input.value = ''
        value_input.value = ''
        description_input.value = ''

def del_component(index):
    #    table.data = [1]
  #  print(list(ui.table.row))
# Подключение к БД
    conn = sqlite3.connect(nameDB)
    cursor = conn.cursor()
    try:
         # Удаление элемента по индексу
 #       cursor.execute('DELETE FROM radio_components WHERE id = ?', (table.data[index][0],))
        print(index)
        cursor.execute('DELETE FROM radio_components WHERE id = ?', (index,))
    finally:
        conn.commit()
        show_components.refresh()
   #     table.data.pop(index)
   #     table.update()

@ui.refreshable
def show_components():
    rows = []
    columns = []
    # Подключение к базе данных
    conn = sqlite3.connect(nameDB)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM radio_components')
        components = cursor.fetchall()
        if components:
            columns=[{'name':'id', 'label':'id', 'field': 'id', 'required': True, 'align': 'left'},
                    {'name':'name', 'label':'Наименование','field': 'name', 'sortable': True},
                    {'name':'value', 'label':'Параметр', 'field': 'value','sortable': True},
                    {'name':'description', 'label':'Описание', 'field': 'description','sortable': True}]
            for component in components:
                rows.append({'id':component[0], 'name':component[1], 'value':component[2], 'description':component[3]})
            table = ui.table(
                columns=columns,
                rows=rows,
                row_key='id',
            )
            table.on('rowClick', lambda e: print(e.args[1]))
        else:
            ui.label("Нет данных")
    finally: 
        conn.close()
        #table.on('rowClick', lambda e: ui.label(f'Выбран компонент: {e.args[2]+1}'))
        table.on('rowClick', lambda e: select(e.args[1]['id']))

@ui.refreshable
def select(select):
    global select_comp
    select_comp=select
    print(select_comp)
    ui.label(f' Выбран компонент {select_comp}')

# Проверка на пустое значение наименования при вводе
def on_click():
    comp_name = name_input.value
    if comp_name:
        add_component()
    else:
        ui.notify("Пожалуйста, введите наименование.")


# Интерфейс
ui.page('Радио компоненты')

with ui.tabs() as tabs:
    with ui.tab('Добавить компонент'):
        ui.label('Добавить радио компонент')
        name_input = ui.input('Наименование', placeholder='Введите наименование')
        value_input = ui.input('Параметр', placeholder='Введите параметр')
        description_input = ui.input('Описание', placeholder='Введите описание')
        ui.button('Добавить', on_click=on_click)
    with ui.tab('Список компонентов'):
        ui.label('Список радио компонентов')
        output = ui.label('')
        with ui.row():
                ui.button('Обновить список', on_click=show_components.refresh)
                ui.button('Удалить выбранный компонент', on_click=lambda: del_component(select_comp))
        show_components()
    with ui.tab('Управление'):
        output = ui.label('')
        ui.button('Новая база данных', on_click=newDB)
        ui.button('Удалить базу данных', on_click=delDB)
        ui.button('Добавить тестовые компоненты', on_click=add_test)
ui.run()

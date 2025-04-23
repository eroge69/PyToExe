import sqlite3
import datetime
import PySimpleGUI as sg

# Подключение к базе данных
conn = sqlite3.connect('oil_change.db')
c = conn.cursor()

# Создание таблицы
c.execute('''CREATE TABLE IF NOT EXISTS machines
             (id INTEGER PRIMARY KEY,
              name TEXT,
              last_oil_change_date DATE,
              work_hours_since_change INTEGER)''')
conn.commit()

# Настройка темы интерфейса
try:
    sg.theme('LightGrey1')
except AttributeError:
    sg.ChangeLookAndFeel('LightGrey1')

def add_machine_window():
    layout = [
        [sg.Text('Добавление нового станка', font=('Helvetica', 16))],
        [sg.Text('Название станка:'), sg.Input(key='-NAME-')],
        [sg.Text('Дата последней замены (ГГГГ-ММ-ДД):'), sg.Input(key='-DATE-')],
        [sg.Text('Рабочих часов с замены:'), sg.Input(key='-HOURS-')],
        [sg.Button('Добавить'), sg.Button('Отмена')]
    ]
    
    window = sg.Window('Добавить станок', layout)
    
    while True:
        event, values = window.read()
        if event in (None, 'Отмена'):
            break
            
        if event == 'Добавить':
            try:
                # Валидация данных
                if not values['-NAME-']:
                    raise ValueError("Не указано название станка")
                    
                datetime.datetime.strptime(values['-DATE-'], "%Y-%m-%d")
                hours = int(values['-HOURS-'])
                
                if hours < 0:
                    raise ValueError("Часы работы не могут быть отрицательными")
                
                # Добавление в БД
                c.execute("INSERT INTO machines (name, last_oil_change_date, work_hours_since_change) VALUES (?, ?, ?)",
                         (values['-NAME-'].strip(), values['-DATE-'], hours))
                conn.commit()
                sg.popup('Станок успешно добавлен!')
                break
                
            except ValueError as e:
                sg.popup_error('Ошибка ввода!', str(e))
            except Exception as e:
                sg.popup_error('Ошибка базы данных!', str(e))
    
    window.close()

def update_oil_change_window():
    machines = get_all_machines()
    if not machines:
        sg.popup('Нет станков в базе')
        return
    
    layout = [
        [sg.Text('Обновление замены масла', font=('Helvetica', 16))],
        [sg.Text('Выберите станок:')],
        [sg.Table(values=machines,
                 headings=['ID', 'Название', 'Последняя замена', 'Часы'],
                 key='-TABLE-',
                 enable_events=True,
                 auto_size_columns=False,
                 col_widths=[5, 20, 15, 10],
                 display_row_numbers=False)],
        [sg.Text('Новая дата замены (ГГГГ-ММ-ДД):'), sg.Input(key='-NEW_DATE-')],
        [sg.Button('Обновить'), sg.Button('Отмена')]
    ]
    
    window = sg.Window('Обновить замену масла', layout)
    selected_id = None
    
    while True:
        event, values = window.read()
        if event in (None, 'Отмена'):
            break
            
        if event == '-TABLE-':
            selected_id = machines[values['-TABLE-'][0]][0]
            
        if event == 'Обновить':
            if not selected_id:
                sg.popup_error('Выберите станок!')
                continue
                
            try:
                new_date = values['-NEW_DATE-'] or datetime.date.today().strftime("%Y-%m-%d")
                datetime.datetime.strptime(new_date, "%Y-%m-%d")
                
                c.execute("UPDATE machines SET last_oil_change_date=?, work_hours_since_change=0 WHERE id=?",
                         (new_date, selected_id))
                conn.commit()
                sg.popup('Данные обновлены!')
                break
                
            except ValueError:
                sg.popup_error('Неверный формат даты!')
            except Exception as e:
                sg.popup_error('Ошибка базы данных!', str(e))
    
window.close()

def get_all_machines():
    try:
        c.execute("SELECT * FROM machines")
        return c.fetchall()
    except Exception as e:
        sg.popup_error('Ошибка базы данных!', str(e))
        return []

def view_machines_window():
    machines = get_all_machines()
    if not machines:
        sg.popup('Нет станков в базе')
        return
    
    layout = [
        [sg.Text('Список станков', font=('Helvetica', 16))],
        [sg.Table(values=machines,
                 headings=['ID', 'Название', 'Последняя замена', 'Часы'],
                 auto_size_columns=False,
                 col_widths=[5, 20, 15, 10],
                 justification='left')],
        [sg.Button('Закрыть')]
    ]
    
    window = sg.Window('Просмотр станков', layout)
    window.read()
    window.close()

def check_maintenance_window():
    machines = get_all_machines()
    if not machines:
        sg.popup('Нет станков в базе')
        return
    
    today = datetime.date.today()
    warning_machines = []
    
    for machine in machines:
        try:
            last_date = datetime.datetime.strptime(machine[2], "%Y-%m-%d").date()
            days_passed = (today - last_date).days
            hours = machine[3]
            
            if days_passed > 30 or hours > 500:
                warning_machines.append([
                    machine[0], 
                    machine[1],
                    f'{days_passed} дней (>30)' if days_passed > 30 else '',
                    f'{hours} часов (>500)' if hours > 500 else ''
                ])
        except Exception as e:
            sg.popup_error('Ошибка данных!', f"Ошибка в записи станка ID {machine[0]}: {str(e)}")
    
    if not warning_machines:
        sg.popup('Все станки в норме!')
        return
    
    layout = [
        [sg.Text('Станки требующие внимания', font=('Helvetica', 16))],
        [sg.Table(values=warning_machines,
                 headings=['ID', 'Название', 'Дни с замены', 'Часы работы'],
                 auto_size_columns=False,
                 col_widths=[5, 20, 15, 15])],
        [sg.Button('Закрыть')]
    ]
    
    window = sg.Window('Проверка обслуживания', layout)
    window.read()
    window.close()

def main_window():
    menu_layout = [
        [sg.Button('Добавить станок', size=(20, 2), pad=(10, 10))],
        [sg.Button('Обновить замену масла', size=(20, 2), pad=(10, 10))],
        [sg.Button('Просмотреть все станки', size=(20, 2), pad=(10, 10))],
        [sg.Button('Проверить обслуживание', size=(20, 2), pad=(10, 10))],
        [sg.Button('Выход', size=(20, 2), pad=(10, 10))]
    ]
    
    layout = [
        [sg.Text('Система учёта замены масла', 
                font=('Helvetica', 20), 
                justification='center',
                pad=(10, 20))],
        [sg.Column(menu_layout, 
                 element_justification='center',
                 pad=(0, 20))]
    ]
    
    window = sg.Window('Учёт замены масла', 
                      layout, 
                      element_justification='center',
                      finalize=True)
    
    while True:
        event, values = window.read()
        if event in (None, 'Выход'):
            break
            
        try:
            if event == 'Добавить станок':
                add_machine_window()
            elif event == 'Обновить замену масла':
                update_oil_change_window()
            elif event == 'Просмотреть все станки':
                view_machines_window()
            elif event == 'Проверить обслуживание':
                check_maintenance_window()
        except Exception as e:
            sg.popup_error('Критическая ошибка!', str(e))
    
    window.close()
    conn.close()

if name == "main":  # Исправленная строка
    main_window()
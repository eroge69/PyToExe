import flet as ft
import random
import time
import csv

def main(page: ft.Page):
    page.title = 'Test'
    page.theme_mode = 'dark'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    string_rus_letters='АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЭЮЯ'

    def on_keyboard(e: ft.KeyboardEvent):
        try:
            d=ft.Text(f"Key: {e.key}")
            global klav
            klav.append([str(d.value), time.time()-start_time])
        except:
            global error
            error+=1
        #print(str(d.value))

    def mas_new(mas):
        i=0
        while i<len(mas):
            mas[i] = [i] + mas[i]
            i+=1
        mas = [['N', 'number_square', 'letter', 'color', 'start_time_letter']] + mas
        return(mas)

    def change_stop(e):
        global st
        st = 1
        global click_stop
        click_stop.append([st, time.time() - start_time])

    def save_mas(mas, qw):
        name_file = str(name.value) + '_' + str(age.value) + '_' + str(date.value)
        if qw == 1:
            name_file = str(name_file) + '_' + 'kw_1.csv'
        elif qw == 2:
            name_file = str(name_file) + '_' + 'kw_2.csv'
        elif qw == 3:
            name_file = str(name_file) + '_' + 'kw_3.csv'
        elif qw == 4:
            name_file = str(name_file) + '_' + 'kw_4.csv'
        elif qw == 5:
            name_file = str(name_file) + '_' + 'kw_all.csv'
        elif qw == 6:
            name_file = str(name_file) + '_' + 'click_stop.csv'
        elif qw == 7:
            name_file = str(name_file) + '_' + 'klav.csv'
        with open(name_file, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in mas:
                writer.writerow(row)
        

    def change_v(e):
        page.controls.pop()
        page.add(panel_test)
        page.update()
        x=0
        color_choice = [ft.colors.RED, ft.colors.INDIGO]
        global start_time
        start_time=time.time()
        kw_1=[]
        kw_2=[]
        kw_3=[]
        kw_4=[]
        kw_all=[]
        global click_stop
        click_stop = []
        global st
        st = 0
        global klav
        klav = []
        while x<7200:
            if st == 0:
                text_b_1.value = random.choice(string_rus_letters)
                text_b_2.value = ''
                text_b_3.value = ''
                text_b_4.value = ''
                text_b_1.color = random.choice(color_choice)
            
                page.update()
                click_stop.append([st, time.time() - start_time])
                kw_1.append(['1', text_b_1.value, text_b_1.color, time.time() - start_time])
                kw_all.append(['1', text_b_1.value, text_b_1.color, time.time() - start_time])
                click_stop.append([st, time.time() - start_time])

                x=execution_time = time.time() - start_time
                

                i=0
                while i<25000000:
                    i+=1
     
                x=execution_time = time.time() - start_time
                #print(st)

                text_b_2.value = random.choice(string_rus_letters)
                text_b_1.value = ''
                text_b_3.value = ''
                text_b_4.value = ''
                text_b_2.color = random.choice(color_choice)

                page.update()
                click_stop.append([st, time.time() - start_time])
                kw_2.append(['2', text_b_2.value, text_b_2.color, time.time() - start_time])
                kw_all.append(['2', text_b_2.value, text_b_2.color, time.time() - start_time])
                click_stop.append([st, time.time() - start_time])

                x=execution_time = time.time() - start_time
                #print(st)

                i=0
                while i<25000000:
                    i+=1

                x=execution_time = time.time() - start_time
                #print(st)

                text_b_4.value = random.choice(string_rus_letters)
                text_b_2.value = ''
                text_b_1.value = ''
                text_b_3.value = ''
                text_b_4.color = random.choice(color_choice)

                page.update()
                click_stop.append([st, time.time() - start_time])
                kw_3.append(['3', text_b_4.value, text_b_4.color, time.time() - start_time])
                kw_all.append(['3', text_b_4.value, text_b_4.color, time.time() - start_time])
                click_stop.append([st, time.time() - start_time])

                x=execution_time = time.time() - start_time
                #print(st)

                i=0
                while i<25000000:
                    i+=1

                x=execution_time = time.time() - start_time
                #print(st)

                text_b_3.value = random.choice(string_rus_letters)
                text_b_2.value = ''
                text_b_4.value = ''
                text_b_1.value = ''
                text_b_3.color = random.choice(color_choice)

                page.update()
                click_stop.append([st, time.time() - start_time])
                kw_4.append(['4', text_b_3.value, text_b_3.color, time.time() - start_time])
                kw_all.append(['4', text_b_3.value, text_b_3.color, time.time() - start_time])
                click_stop.append([st, time.time() - start_time])

                x=execution_time = time.time() - start_time
                #print(st)
                i=0
                while i<25000000:
                    i+=1
            
                x=execution_time = time.time() - start_time
                #print(st)

            else:
                break

        #print('kw_1[0]: ', kw_1[0])
        #print('kw_2: ', kw_2)
        #print('kw_3: ', kw_3)
        #print('kw_4: ', kw_4)
        #print('click_stop', click_stop)
        #print('klav', klav)
        #print('kw_all', kw_all)
        #print('kw_all[1]', kw_all[1])

        kw_1 = mas_new(kw_1)
        kw_2 = mas_new(kw_2)
        kw_3 = mas_new(kw_3)
        kw_4 = mas_new(kw_4)
        kw_all = mas_new(kw_all)
        i=0
        while i<len(click_stop):
            click_stop[i] = [i] + click_stop[i]
            i+=1
        click_stop = [['N', 'stop_button', 'time']] + click_stop
        #print(kw_1[0])
        i=0
        while i<len(klav):
            klav[i] = [i] + klav[i]
            i+=1
        klav = [['N', 'key', 'click_time']] + klav

        save_mas(kw_1, 1)
        save_mas(kw_2, 2)
        save_mas(kw_3, 3)
        save_mas(kw_4, 4)
        save_mas(kw_all, 5)
        save_mas(click_stop, 6)
        save_mas(klav, 7)

        name.value = ''
        age.value = ''
        date.value = ''

        page.controls.pop()
        page.add(panel_nach)
        page.update()
    
    text_b_1 = ft.Text(value='', size=100, color = ft.colors.WHITE)
    text_b_2 = ft.Text(value='', size=100, color = ft.colors.WHITE)
    text_b_3 = ft.Text(value='', size=100, color = ft.colors.WHITE)
    text_b_4 = ft.Text(value='', size=100, color = ft.colors.WHITE)
    global error
    error = 0

    panel_test = ft.Column([
        ft.Row([
            ft.Container(
                content=text_b_1,
                bgcolor=ft.colors.WHITE,
                alignment=ft.alignment.center,
                width=155,
                height=155,
                border=ft.border.all(5, ft.colors.WHITE),
                ),

            ft.Container(
                content=text_b_2,
                bgcolor=ft.colors.WHITE,
                alignment=ft.alignment.center,
                width=155,
                height=155,
                border=ft.border.all(5, ft.colors.WHITE),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row([
            ft.Container(
                content=text_b_3,
                bgcolor=ft.colors.WHITE,
                alignment=ft.alignment.center,
                width=155,
                height=155,
                border=ft.border.all(5, ft.colors.WHITE),
                ),

            ft.Container(
                content=text_b_4,
                bgcolor=ft.colors.WHITE,
                alignment=ft.alignment.center,
                width=155,
                height=155,
                border=ft.border.all(5, ft.colors.WHITE),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row([ft.OutlinedButton('stop', on_click=change_stop),], alignment=ft.MainAxisAlignment.END),
        ],
            )

    #panel_nach = ft.Row([
    #        ft.OutlinedButton('Начать', on_click=change_v),
    #        ],
    #        alignment=ft.MainAxisAlignment.CENTER
    #    )

    name = ft.TextField(label="Имя")
    age = ft.TextField(label="Возраст")
    date = ft.TextField(label="Дата эксперимента")

    panel_nach = ft.Column([
        ft.Row([name,],alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([age,],alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([date,],alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([ft.OutlinedButton('Начать', on_click=change_v),], alignment=ft.MainAxisAlignment.CENTER),
        ])


    page.on_keyboard_event = on_keyboard
    page.add(panel_nach)

ft.app(target=main)

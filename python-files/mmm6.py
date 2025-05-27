
import os

import time

import logging

import win32com.client

import pandas as pd

from datetime import datetime



# Настройка логирования

logging.basicConfig(

    filename="outlook_launcher1.log",

    level=logging.DEBUG,  # DEBUG для более детальной информации

    format="%(asctime)s - %(levelname)s - %(message)s",

)

def read_signature():

    signature_path = r"C:\Users\kuliev.ea\AppData\Roaming\Microsoft\Signatures\2.htm"



    if not os.path.exists(signature_path):

        logging.warning(f"Файл подписи не найден по пути: {signature_path}")

        return ""



    try:

        with open(signature_path, "r", encoding="utf-8") as file:

            return file.read()

    except UnicodeDecodeError:

        try:

            with open(signature_path, "r", encoding="cp1251") as file:

                return file.read()

        except Exception as e:

            logging.error(f"Ошибка при чтении подписи: {str(e)}")

            return ""



signature = read_signature()



def get_month_cases():

    months = {

        1: ("январь", "в январе"),

        2: ("февраль", "в феврале"),

        3: ("март", "в марте"),

        4: ("апрель", "в апреле"),

        5: ("май", "в мае"),

        6: ("июнь", "в июне"),

        7: ("июль", "в июле"),

        8: ("август", "в августе"),

        9: ("сентябрь", "в сентябре"),

        10: ("октябрь", "в октябре"),

        11: ("ноябрь", "в ноябре"),

        12: ("декабрь", "в декабре")

    }

    current_month = datetime.now().month

    return months[current_month]



def launch_outlook():

    try:

        # Путь к excel файлу

        excel_path = r"C:\Users\kuliev.ea\Desktop\Питон\dann.xlsx"



        # Читаем данные из excel

        logging.info("Читаем данные из Excel...")

        df = pd.read_excel(

            excel_path,

            sheet_name=0,

            usecols=["Код ИСУП", "FTE", "Наименование", "Менеджер продукта"]

        )



        # Получаем падежи месяца

        month_nominative, month_genitive = get_month_cases()



        # Создаем Outlook один раз

        logging.info("Создаем приложение Outlook...")

        outlook = win32com.client.Dispatch("Outlook.Application")



        # Проходим по всем строкам DataFrame

        created_emails = 0  # Добавляем счетчик писем



        for index, row in df.iterrows():

            # Получаем значения из текущей строки

            code_ISUP = row["Код ИСУП"]

            fte = row["FTE"]

            name = row["Наименование"]

            recipient = row["Менеджер продукта"]



            # Создаем новое письмо

            mail = outlook.CreateItem(0)  # 0 - это тип нового письма



            # Устанавливаем тему письма

            mail.Subject = f"Списание ТРЗ {code_ISUP} за {month_nominative}"



            # Форматируем письмо в HTML

            mail.BodyFormat = 2  # Устанавливаем HTML формат

            mail.Body = (

                f'Добрый день.\n\n'  # Добрый день и пустая строка

                f'Прошу подтвердить:\n\n'  # Пустая строка

                f'1. Потребность привлечения меня на проект в качестве специалиста по ИБ в {month_genitive}.\n\n'  # Пустая строка

                f'2. Наличие бюджета для списания ТРЗ в объем {fte} FTE на проект {code_ISUP} {name} {month_genitive};\n\n'  # Пустая строка

                f'3. В случае наличия возможности списания – прошу уточнить, списание предполагается за счет проекта {code_ISUP} или иного?\n\n'

            )

            # Добавляем подпись

            if signature:

                mail.HTMLBody += signature

            else:

                try:

                    # Получаем объект WordEditor

                    word = mail.GetInspector.WordEditor

                    # Добавляем пустую строку перед подписью

                    word.Application.Selection.TypeParagraph()

                    # Добавляем стандартную подпись

                    word.Application.ActiveDocument.SignatureLine.Insert(

                        1, "Подпись", "Подпись"

                    )

                except Exception as e:

                    logging.warning(f"Ошибка при добавлении подписи: {str(e)}")



            # Устанавливаем адресата

            mail.To = recipient



            try:

                # Отправляем письмо

                mail.Send()

                logging.info(f"Письмо успешно отправлено: {recipient}")

            except Exception as e:

                logging.error(f"Ошибка при отправке письма: {str(e)}")



            # Добавляем счетчик созданных писем

            created_emails += 1



            # Ждем немного перед созданием следующего письма

            time.sleep(0)



            logging.info(f"Создано и отправлено {created_emails} писем")



        return True



    except Exception as e:

        logging.error(f"Ошибка при запуске Outlook: {str(e)}")

        return False

if __name__ == "__main__":

    print("Запуск отправки писем...")

    try:

        if launch_outlook():

            print("Все письма успешно отправлены!")

        else:

            print("Ошибка при отправке писем. Проверьте логи для деталей.")

    except Exception as e:

            print(f"Произошла ошибка: {str(e)}")



    # Добавляем паузу, чтобы пользователь успел увидеть сообщение

input("Ебаните Enter для выхода...")

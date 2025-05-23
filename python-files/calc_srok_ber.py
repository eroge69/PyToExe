#!/usr/bin/env python3
from datetime import date

def calculate_whole_weeks(f3_date):
    today = date.today()
    delta = today - f3_date
    whole_weeks = delta.days // 7
#    whole_days = delta.days % 7
    return whole_weeks

def calculate_whole_days(f3_date):
    today = date.today()
    delta = today - f3_date
    whole_days = delta.days % 7
    return whole_days

day_to_die = int(input('День последней менструации: '))
month_to_die = int(input('Месяц последней менструации: '))
year_to_die  = int(input('Год последней менструации: '))
f3_date = date(year_to_die, month_to_die, day_to_die)
weeks = calculate_whole_weeks(f3_date)
days = calculate_whole_days(f3_date)
print(f'Срок беременности на сегодня {weeks} недель(и) {days} дня(ей).')
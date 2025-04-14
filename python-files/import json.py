import json
import os
from datetime import datetime

class Employee:
    def __init__(self, last_name, first_name, patronymic, position, hire_date, passport, education, address, experience):
        self.last_name = last_name
        self.first_name = first_name
        self.patronymic = patronymic
        self.position = position
        self.hire_date = hire_date
        self.passport = passport
        self.education = education
        self.address = address
        self.experience = experience

class Unemployed:
    def __init__(self, last_name, first_name, patronymic, desired_position, registration_date, passport, education, address, benefits):
        self.last_name = last_name
        self.first_name = first_name
        self.patronymic = patronymic
        self.desired_position = desired_position
        self.registration_date = registration_date
        self.passport = passport
        self.education = education
        self.address = address
        self.benefits = benefits

class Company:
    def __init__(self, name, address, industry, vacancies):
        self.name = name
        self.address = address
        self.industry = industry
        self.vacancies = vacancies

class Vacancy:
    def __init__(self, position, salary, requirements, experience_required):
        self.position = position
        self.salary = salary
        self.requirements = requirements
        self.experience_required = experience_required

class EmploymentCenter:
    def __init__(self):
        self.employees = []
        self.unemployed = []
        self.companies = []
        self.vacancies = []
        
        # Загрузка данных при инициализации
        self.load_data()
    
    def save_data(self):
        data = {
            'employees': [vars(emp) for emp in self.employees],
            'unemployed': [vars(unemp) for unemp in self.unemployed],
            'companies': [vars(comp) for comp in self.companies],
            'vacancies': [vars(vac) for vac in self.vacancies]
        }
        
        with open('employment_center_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def load_data(self):
        if os.path.exists('employment_center_data.json'):
            with open('employment_center_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.employees = [Employee(**emp) for emp in data.get('employees', [])]
                self.unemployed = [Unemployed(**unemp) for unemp in data.get('unemployed', [])]
                self.companies = [Company(**comp) for comp in data.get('companies', [])]
                self.vacancies = [Vacancy(**vac) for vac in data.get('vacancies', [])]
    
    def add_employee(self):
        print("\nДобавление нового сотрудника:")
        last_name = input("Фамилия: ")
        first_name = input("Имя: ")
        patronymic = input("Отчество: ")
        position = input("Должность: ")
        hire_date = input("Дата приема на работу (ГГГГ-ММ-ДД): ")
        passport = input("Паспортные данные: ")
        education = input("Образование: ")
        address = input("Адрес: ")
        experience = float(input("Стаж работы (лет): "))
        
        employee = Employee(last_name, first_name, patronymic, position, hire_date, passport, education, address, experience)
        self.employees.append(employee)
        self.save_data()
        print("Сотрудник успешно добавлен!")
    
    def add_unemployed(self):
        print("\nДобавление нового безработного:")
        last_name = input("Фамилия: ")
        first_name = input("Имя: ")
        patronymic = input("Отчество: ")
        desired_position = input("Желаемая должность: ")
        registration_date = input("Дата регистрации (ГГГГ-ММ-ДД): ")
        passport = input("Паспортные данные: ")
        education = input("Образование: ")
        address = input("Адрес: ")
        benefits = float(input("Размер пособия: "))
        
        unemployed = Unemployed(last_name, first_name, patronymic, desired_position, registration_date, passport, education, address, benefits)
        self.unemployed.append(unemployed)
        self.save_data()
        print("Безработный успешно зарегистрирован!")
    
    def add_company(self):
        print("\nДобавление нового предприятия:")
        name = input("Название предприятия: ")
        address = input("Адрес предприятия: ")
        industry = input("Отрасль: ")
        vacancies = []
        
        while True:
            add_vacancy = input("Добавить вакансию? (да/нет): ").lower()
            if add_vacancy != 'да':
                break
                
            position = input("Должность: ")
            salary = float(input("Зарплата: "))
            requirements = input("Требования: ")
            experience_required = float(input("Требуемый стаж (лет): "))
            
            vacancy = Vacancy(position, salary, requirements, experience_required)
            vacancies.append(vacancy)
            self.vacancies.append(vacancy)
        
        company = Company(name, address, industry, vacancies)
        self.companies.append(company)
        self.save_data()
        print("Предприятие успешно добавлено!")
    
    def show_employees_by_experience(self):
        try:
            min_experience = float(input("\nВведите минимальный стаж работы (лет): "))
            filtered_employees = [emp for emp in self.employees if emp.experience >= min_experience]
            
            if not filtered_employees:
                print("Нет сотрудников с таким стажем работы.")
                return
                
            print(f"\nСотрудники со стажем работы {min_experience} лет и более:")
            for emp in filtered_employees:
                print(f"{emp.last_name} {emp.first_name} {emp.patronymic} - {emp.position} (стаж: {emp.experience} лет)")
        except ValueError:
            print("Ошибка: введите корректное число для стажа.")
    
    def search_employee_by_last_name(self):
        last_name = input("\nВведите фамилию сотрудника для поиска: ")
        found_employees = [emp for emp in self.employees if emp.last_name.lower() == last_name.lower()]
        
        if not found_employees:
            print("Сотрудник с такой фамилией не найден.")
            return
            
        print("\nНайденные сотрудники:")
        for emp in found_employees:
            print("\nИнформация о сотруднике:")
            print(f"ФИО: {emp.last_name} {emp.first_name} {emp.patronymic}")
            print(f"Должность: {emp.position}")
            print(f"Дата приема на работу: {emp.hire_date}")
            print(f"Паспортные данные: {emp.passport}")
            print(f"Образование: {emp.education}")
            print(f"Адрес: {emp.address}")
            print(f"Стаж работы: {emp.experience} лет")
    
    def sort_data(self):
        print("\nСортировка данных:")
        print("1. Сортировка сотрудников по фамилии")
        print("2. Сортировка сотрудников по стажу")
        print("3. Сортировка безработных по фамилии")
        print("4. Сортировка вакансий по зарплате")
        
        choice = input("Выберите вариант сортировки: ")
        
        if choice == '1':
            sorted_employees = sorted(self.employees, key=lambda x: x.last_name)
            print("\nСотрудники, отсортированные по фамилии:")
            for emp in sorted_employees:
                print(f"{emp.last_name} {emp.first_name} - {emp.position}")
                
        elif choice == '2':
            sorted_employees = sorted(self.employees, key=lambda x: x.experience, reverse=True)
            print("\nСотрудники, отсортированные по стажу (по убыванию):")
            for emp in sorted_employees:
                print(f"{emp.last_name} - стаж {emp.experience} лет")
                
        elif choice == '3':
            sorted_unemployed = sorted(self.unemployed, key=lambda x: x.last_name)
            print("\nБезработные, отсортированные по фамилии:")
            for unemp in sorted_unemployed:
                print(f"{unemp.last_name} {unemp.first_name} - ищет работу {unemp.desired_position}")
                
        elif choice == '4':
            sorted_vacancies = sorted(self.vacancies, key=lambda x: x.salary, reverse=True)
            print("\nВакансии, отсортированные по зарплате (по убыванию):")
            for vac in sorted_vacancies:
                print(f"{vac.position} - {vac.salary} руб. (требуемый стаж: {vac.experience_required} лет)")
                
        else:
            print("Неверный выбор.")
    
    def import_from_file(self):
        filename = input("Введите имя файла для импорта (например, data.json): ")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.employees = [Employee(**emp) for emp in data.get('employees', [])]
                self.unemployed = [Unemployed(**unemp) for unemp in data.get('unemployed', [])]
                self.companies = [Company(**comp) for comp in data.get('companies', [])]
                self.vacancies = [Vacancy(**vac) for vac in data.get('vacancies', [])]
                
                self.save_data()
                print("Данные успешно импортированы из файла!")
        except FileNotFoundError:
            print("Файл не найден.")
        except json.JSONDecodeError:
            print("Ошибка чтения файла. Убедитесь, что это корректный JSON-файл.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
    
    def export_to_file(self):
        filename = input("Введите имя файла для экспорта (например, export.json): ")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                data = {
                    'employees': [vars(emp) for emp in self.employees],
                    'unemployed': [vars(unemp) for unemp in self.unemployed],
                    'companies': [vars(comp) for comp in self.companies],
                    'vacancies': [vars(vac) for vac in self.vacancies]
                }
                json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Данные успешно экспортированы в файл {filename}!")
        except Exception as e:
            print(f"Произошла ошибка при экспорте: {str(e)}")
    
    def show_statistics(self):
        print("\nСтатистика центра занятости:")
        print(f"Количество зарегистрированных сотрудников: {len(self.employees)}")
        print(f"Количество зарегистрированных безработных: {len(self.unemployed)}")
        print(f"Количество предприятий: {len(self.companies)}")
        print(f"Количество вакансий: {len(self.vacancies)}")
        
        if self.unemployed:
            avg_benefits = sum(unemp.benefits for unemp in self.unemployed) / len(self.unemployed)
            print(f"Средний размер пособия по безработице: {avg_benefits:.2f}")
        
        if self.vacancies:
            avg_salary = sum(vac.salary for vac in self.vacancies) / len(self.vacancies)
            print(f"Средняя зарплата по вакансиям: {avg_salary:.2f}")

def main():
    center = EmploymentCenter()
    
    while True:
        print("\n=== Центр занятости населения ===")
        print("1. Добавить сотрудника")
        print("2. Добавить безработного")
        print("3. Добавить предприятие с вакансиями")
        print("4. Показать сотрудников с определенным стажем")
        print("5. Найти сотрудника по фамилии")
        print("6. Сортировка данных")
        print("7. Импорт данных из файла")
        print("8. Экспорт данных в файл")
        print("9. Показать статистику")
        print("0. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            center.add_employee()
        elif choice == '2':
            center.add_unemployed()
        elif choice == '3':
            center.add_company()
        elif choice == '4':
            center.show_employees_by_experience()
        elif choice == '5':
            center.search_employee_by_last_name()
        elif choice == '6':
            center.sort_data()
        elif choice == '7':
            center.import_from_file()
        elif choice == '8':
            center.export_to_file()
        elif choice == '9':
            center.show_statistics()
        elif choice == '0':
            print("Работа программы завершена.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
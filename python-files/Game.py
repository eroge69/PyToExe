import random

def guess_number():
    secret_number = random.randint(1, 60)
    attempts = 6
    
    print("����� ���������� � ���� '������ �����'!")
    print("� ������� ����� �� 1 �� 60. � ��� ���� 6 �������.")
    
    for attempt in range(1, attempts + 1):
        try:
            guess = int(input(f"������� {attempt}: ������� �����: "))
            
            if guess < 1 or guess > 60:
                print("����������, ������� ����� � ��������� �� 1 �� 60!")
                continue
            
            if guess == secret_number:
                print(f"�����������! �� ������� ����� � {attempt} �������!")
                return
            elif guess < secret_number:
                print("���������� ����� ������!")
            else:
                print("���������� ����� ������!")
                
        except ValueError:
            print("����������, ������� ���������� �����!")
            continue
            
    print(f"� ���������, �� �� �������. ���������� ����� ���� {secret_number}")

guess_number()

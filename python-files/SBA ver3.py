import random
import math
import os
record=[]
a=["","",0,0,""]*10
grouping_record=[a]*9
found=False
count=0
target=""
password=""
uid=""
en_con=random.randint(1,10)
e_pw=""
e_in_pw=""
c0=0
c1=0
c2=0
def category():
    cat=int(input("Choose the category that you want to sort by:\n0->name\n1->sex\n2->year_of_graduation\n3->number_of_seats_require\nPlease input your choice:"))
    while cat <= -1 or cat >=4:
        print("There is only four choice")
        cat=int(input("Please input again\n0->name\n1->sex\n2->year_of_graduation\n3->number_of_seats_require\nPlease input your choice:"))
    return cat
def a_o_d():
    a_o_d=int(input("Show ascending order or descending order\n1->ascending order\n2->descending order\nPlease input your choice:"))
    while a_o_d <= 0 or a_o_d >=3:
        print("There is only two choice")
        a_o_d=int(input("Please input again\n1->ascending order\n2->descending order\nPlease input your choice:"))
    return a_o_d
def partition(array, low, high,cat):
    pivot = array[high][cat]
    i = low - 1
    for j in range(low, high):
        if array[j][cat] <= pivot:
            i = i + 1
            (array[i], array[j]) = (array[j], array[i])
    (array[i + 1], array[high]) = (array[high], array[i + 1])
    return i + 1

def quickSort(array, low, high, cat):
  if low < high:
    pi = partition(array, low, high, cat)
    quickSort(array, low, pi - 1, cat)
    quickSort(array, pi + 1, high, cat)

def sort(cat):
    size = len(record)
    quickSort(record, 0, size - 1,cat)

def encode_og(pw):
    global e_pw
    for i in range(len(pw)):
        e_pw+=chr(ord(pw[i])+en_con)

def encode_in(in_pw):
    global e_in_pw
    for i in range(len(in_pw)):
        e_in_pw+=chr(ord(in_pw[i])+en_con)

def search_record_uid(target):
    global i
    for i in range(0,len(record)):
        if record[i][4]==target:
            return i
    return -1

def binary(target,cat):
    global found
    found=False 
    start=0
    end=len(record)-1
    while start <= end and found == False:
        mid=int((start+end)/2)
        if record[mid][cat] == target:
            found = True
        else:
            if target < record[mid][cat]:
                end=mid-1
            else:
                start=mid+1
    return found,mid

def update_file():
    f=open("Dinner.txt","w")
    for i in range(0,len(record)):
        f.write(record[i][0]+";"+record[i][1]+";"+record[i][2]+";"+record[i][3]+";"+record[i][4])
        if i < len(record)-1:
            f.write("\n")

def load_record():
    f=open("Dinner.txt",'r')
    global record
    record=f.readlines()
    for i in range(0,len(record)):
        record[i]=record[i].replace("\n","")
        record[i]=record[i].split(";")
    f.close()

def load_password():
    f=open("password.txt",'r')
    global password
    password=f.readline()
    f.close()

def print_record(a_o_d):
    if a_o_d == 1:
        for i in range(0,len(record)):
            for j in range(0,5):
                print(record[i][j],end="\t")
            print("")
    elif a_o_d == 2:
        for i in range(len(record)-1,-1,-1):
            for j in range(0,5):
                print(record[i][j],end="\t")
            print("")

def add_record(fn,sex,y_o_g,n_o_s_r,uid):
    f=open("Dinner.txt","a")
    f.write("\n"+fn+";"+sex+";"+y_o_g+";"+n_o_s_r+";"+uid)
    f.close

def amend_record(uid,fn,sex,y_o_g,n_o_s_r):
    i=search_record_uid(uid)
    if i != -1 :
        record[i][0]=fn
        record[i][1]=sex
        record[i][2]=y_o_g
        record[i][3]=n_o_s_r
    update_file()

def del_record(uid):
    row=search_record_uid(uid)
    if row!=-1:
        for j in range(0,3):
            global record
            record[row][j]=record[row+1][j]
        record.pop()
        print("Record deleted successfully!")
    else:
        print("SORRY! There is no such that person")
    update_file()
def input_thing():
    fn=input("Please input your name(Full Name)(input -1 for exit this mode):")
    if fn != "-1":
        sex=input("Please input your sex(M/F)(input -1 for exit this mode):")
        if sex == "m" or sex == "f":
            sex=chr(ord(sex)+32)
        while sex != "M" and sex != "F" and sex != "-1":#validation check
            sex=input("Please input your sex again(M/F)(input -1 for exit this mode):")
        if sex != "-1":
            y_o_g=input("Please input your year of graduation(year>1984)(input -1 for exit this mode):")
            while int(y_o_g)<1985 and y_o_g != "-1":
                print("You should have study in STTSS at least 1 year")
                y_o_g=input("Please input your year of graduation again(input -1 for exit this mode):")
            if y_o_g != "-1":
                n_o_s_r=input("Please input the number of seats required(1 - 5)(input -1 for exit this mode):")
                while not(int(n_o_s_r)>0 or int(n_o_s_r)<6):
                    if n_o_s_r != "-1":
                        n_o_s_r=input("Please input the number of seats required again(input -1 for exit this mode):")
                    else:
                        break
                if n_o_s_r == "-1":
                    fn,sex,y_o_g,n_o_s_r="-1","-1","-1","-1"
            else:
                fn,sex,y_o_g,n_o_s_r="-1","-1","-1","-1"
        else:
            fn,sex,y_o_g,n_o_s_r="-1","-1","-1","-1"            
    else:
        fn,sex,y_o_g,n_o_s_r="-1","-1","-1","-1"
    return fn,sex,y_o_g,n_o_s_r
def main_menu():
    print('''     Main Menu
===================
1.......Use as User
2......Use as Admin
3..Leave the system
''')

def print_menu1():
    print(''' Choose a function
===================
1.....adding record
2.....search record
3.back to main menu
''')

def print_menu2():
    print('''       Welcome back admin
================================
1................printing record
2..................adding record
3.................amend a record
4................delete a record
5................search a record
6.......................grouping
7..log out and back to main menu
''')

def generate_uid():
    for i in range(0,4):
        uid=chr(random.randint(65, 90))
        uid+=chr(random.randint(97, 122))
        uid+=chr(random.randint(48, 57))
        uid+=chr(random.randint(48, 57))
    return uid

def parse_records(record_list):
    parsed = []
    for r in record_list:
        fn, sex, y_o_g, n_o_s_r, uid = r.strip().split(';')
        parsed.append({
            'fn': fn,
            'sex': sex,
            'y_o_g': int(y_o_g),
            'n_o_s_r': int(n_o_s_r),
            'uid': uid
        })
    return parsed

def smart_grouping(data):
    total = len(data)

    # Try different group counts from sqrt(n) upwards to find a good fit
    best_groups = []
    min_variation = float('inf')

    for num_groups in range(2, total + 1):
        base_size = total // num_groups
        extra = total % num_groups

        max_size = base_size + (extra if 3 > extra > 0 else 0)
        min_size = base_size

        if max_size - min_size <= 3 and 12 > min_size > 8:
            groups = []
            index = 0
            for i in range(num_groups):
                this_size = base_size + (1 if i < extra else 0)
                groups.append(data[index:index + this_size])
                index += this_size

            variation = max_size - min_size
            if variation < min_variation:
                min_variation = variation
                best_groups = groups

            # Stop early if perfectly even
            if variation == 0:
                break

    return best_groups

def export_groups(groups, folder="output"):
    os.makedirs(folder, exist_ok=True)
    for idx, group in enumerate(groups):
        file_path = os.path.join(folder, f"group_{idx+1}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            for person in group:
                f.write(";".join(map(str, person)) + "\n")

def sort_for_grouping(cat):
    record.sort(key=lambda x: x[cat])


load_record()
load_password()
print('''     Welcome to registration system
========================================''')
main_menu()
c0=int(input("Type your choice here(1 - 3):"))
while c0 != 3 :
    if c0 >=4 or c0 <0:#Data validation(range check)
        print("Sorry! We only have 3 function")
        main_menu()
        c0=int(input("Please type your choice again(1 - 3):"))
    if c0==0:
        main_menu()
        c0=int(input("Type your choice here(1 - 3):"))
    if c0 == 1:  
        print_menu1()
        c1=int(input("Please type your choice (1 - 3):"))
        while c1!=3:#User Function
            if c1<=0 or c1>=4:#Data validation(range check)
                print("Sorry! We only have 3 function")
                print_menu1()
                c1=int(input("Please type your choice again(1 - 3):"))
            if c1==1:#add record
                fn,sex,y_o_g,n_o_s_r=input_thing()
                if fn != "-1" or sex != "-1" or y_o_g != "-1" or n_o_s_r != "-1":
                    uid=generate_uid()
                    for i in range(len(record)):
                        if uid==record[i][4]:
                            uid=generate_uid()
                    print("This is your uid:",uid)
                    add_record(fn,sex,y_o_g,n_o_s_r,uid)
                load_record()
                sort(0)
                update_file()
                print_menu1()
                c1=int(input("Please type your choice (1 - 3):"))
            if c1==2:#search record
                s_uid=input("Input your uid(input -1 for exit this mode):")
                while not(ord(s_uid[0])>=65 and ord(s_uid[0])<=90 and (ord(s_uid[1])>=97 and ord(s_uid[1])<=122) and (ord(s_uid[2])>=48 and ord(s_uid[2])<=57) and (ord(s_uid[3])>=48 and ord(s_uid[3])<=57) or s_uid=="-1"):
                    s_uid=input("That is a unvalide uid!\nPlease input your uid(input -1 for exit this mode):")
                if s_uid!="-1":
                    sort(4)
                    f,i=binary(s_uid,4)
                    if f != False :
                        for j in range(0,4):
                            print(record[i][j],end="\t")
                        print("")
                    else:
                        print("There is no such that person")
                print_menu1()
                c1=int(input("Please type your choice (1 - 3):"))
        c0=0
    if c0 == 2:
        in_pw=input("Input the password:")
        encode_og(password)
        encode_in(in_pw)
        if e_pw==e_in_pw:
            print_menu2()
            c2=int(input("Please type your choice (1 - 7):"))
            while (c2!=7):#Admin Function
                if c2<=0 or c2>=8:#Data validation(range check)
                    print("Sorry! We only have 7 function")
                    print_menu2()
                    c2=int(input("Please type your choice again(1 - 3):"))
                if c2==1:#print
                    load_record()
                    cat=category()
                    if cat==1:
                        b_o_g=int(input("Show male or female or both\n0->both\n1->female\n2->male\nPlease input here:"))
                        if b_o_g <=-1 or b_o_g>=3:
                            print("There are only three choice")
                            b_o_g=int(input("Please input again\n0->both\n1->female\n2->male\nPlease input here:"))
                        if b_o_g == 0 :
                            a_o_d=int(input("male on top or female on top\n1->female\n2->male\nPlease input here:"))
                            sort(cat)
                            print_record(a_o_d)
                        elif b_o_g == 1 :
                            cat=category()
                            sort(cat)
                            for i in range(0,len(record)):
                                if record[i][1]=="F":
                                    for j in range(0,5):
                                        print(record[i][j],end="\t")
                                    print("")
                        elif b_o_g == 2:
                            cat=category()
                            sort(cat)
                            for i in range(0,len(record)):
                                if record[i][1]=="M":
                                    for j in range(0,5):
                                        print(record[i][j],end="\t")
                                    print("")
                    else:
                        sort(cat)
                        per=a_o_d()
                        print_record(per)
                    print_menu2()
                    c2=int(input("Please type your choice (1 - 7):"))
                if c2==2:#add
                    fn,sex,y_o_g,n_o_s_r=input_thing()
                    if fn != "-1" or sex != "-1" or y_o_g != "-1" or n_o_s_r != "-1":
                        uid=generate_uid()
                        for i in range(len(record)):
                            if uid==record[i][4]:
                                uid=generate_uid()
                        print("This is your uid:",uid)
                        add_record(fn,sex,y_o_g,n_o_s_r,uid)
                    load_record()
                    sort(0)
                    update_file()
                    print_menu2()
                    c2=int(input("Please type your choice (1 - 7):"))
                if c2==3:#amend
                    sort(4)
                    uid=input("Uid of the record you want to amend(input -1 for exit this mode):")
                    if uid != "-1":
                        fn,sex,y_o_g,n_o_s_r=input_thing()
                        amend_record(uid,fn,sex,y_o_g,n_o_s_r)
                    sort(0)
                    update_file()
                    print_menu2()
                    c2=int(input("Please type your choice (1 - 7):"))
                if c2==4:#delete
                    sort(4)
                    uid=input("Uid of the record you want to delete(input -1 for exit this mode):")
                    if uid != "-1":
                        del_record(uid)
                    print_menu2()
                    update_file()
                    c2=int(input("Please type your choice (1 - 7):"))
                if c2==5:#search
                    cat=category()
                    sort(cat)
                    if cat==0 or cat==1:
                        target=str(input("Please input your target:"))
                        for i in range(len(record)):
                            if record[i][cat]==target:
                                for j in range(5):
                                    print(record[i][j],end=" ")
                                print()
                    elif cat==2 or cat == 3:
                        targat=int(input("Please input your target:"))
                        for i in range(len(record)):
                            if int(record[i][cat])==target:
                                for j in range(5):
                                    print(record[i][j],end=" ")
                                print()
                    print_menu2()
                    c2=int(input("Please type your choice (1 - 7):"))
                if c2==6:#grouping
                    sort(2)
                    groups = smart_grouping(record)  # Change group_size or num_groups if desired
                    export_groups(groups)
                    print_menu2()
                    c2=int(input("Please type your choice (1 - 7):"))
            c0=0
        else:
            print("You Are not the Admin")
            c0=0
print("Good Bye,Have a nice day")
continue_ = True
while (continue_):
    start_page = int(input('Enter the page to start with: '))
    end_page = int(input('Enter the page to end the printing: '))
    init_sheets = int(input('Enter the initial number of sheets in one textbook: '))
    
    flag_of_extra_textbook = False
    flag_of_incorrect_extra_textbook = False
    
    pages_in_textbook = init_sheets * 4
    front = []
    back = []
    
    extra_front = []
    extra_back = []
    
    for cur_pages in range(start_page + pages_in_textbook - 1, end_page + 1,  pages_in_textbook):
        for marker in range(0, pages_in_textbook // 2, 2):
            front.append(cur_pages - marker)
            front.append(cur_pages - pages_in_textbook + marker + 1)
            back.append(cur_pages - pages_in_textbook + marker + 2)
            back.append(cur_pages - marker - 1)
    
    last_textbook_pages = (end_page - start_page + 1) % pages_in_textbook
    last_textbook_init_sheets = (last_textbook_pages + 3) // 4
    
    if last_textbook_pages % 4 != 0:
        flag_of_incorrect_extra_textbook = True
    else:
        if last_textbook_pages != 0:
            flag_of_extra_textbook = True
        for marker in range(0, last_textbook_pages // 2, 2):
            extra_front.append(end_page - marker)
            extra_front.append(end_page - last_textbook_pages + marker + 1)
            extra_back.append(end_page - last_textbook_pages + marker + 2)
            extra_back.append(end_page - marker - 1)
    
    print('Pages to print on the FRONT side of the paper: ', front + extra_front)
    print('Pages to print on the BACK side of the paper: ', back + extra_back)
    if flag_of_incorrect_extra_textbook:
        print('!!!Given pages for printing the last textbook of the book may be printed incorrectly, recommended to use special programms for printing brochure or to update file with clear sheets!!!')
        print('First page in the last textbook: ', end_page - last_textbook_pages + 1)
        print('Last page in the last textbook: ', end_page)
    elif flag_of_extra_textbook:
        print('Number of initial papersheets in the last textbook: ', last_textbook_init_sheets)
        
    front = front + extra_front
    back = back + extra_back
        
    f = open('pages for printing the book', 'w')
    f.write('Pages to print on the FRONT side of the paper: ' + '\n' + '\n')
    for i in range(len(front)):
        if i == 0:
            f.write(str(front[0]))
        else:
            f.write(', ' + str(front[i]))
     
    f.write('\n\nPages to print on the BACK side of the paper: ' + '\n' + '\n')
    for i in range(len(back)):
        if i == 0:
            f.write(str(back[0]))
        else:
            f.write(', ' + str(back[i]))
    f.write('\n\n')
    if flag_of_incorrect_extra_textbook:
        f.write('!!!Given pages for printing the last textbook of the book may be printed incorrectly, recommended to use special programms for printing brochure or to update file with clear sheets!!!' + '\n')
        f.write('First page in the last textbook: ')
        f.write(str(end_page - last_textbook_pages + 1))
        f.write('\n')
        f.write('Last page in the last textbook: ')
        f.write(str(end_page))
    elif flag_of_extra_textbook:
        f.write('Number of initial papersheets in the last textbook: ') 
        f.write(str(last_textbook_init_sheets))
    f.close()
    flag = input('Do you want to continue using programm?(y/n): ')
    continue_ = (flag == 'y')
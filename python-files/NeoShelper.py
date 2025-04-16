import time
print('''__#____#____#________________________
__#____#____#________________________
__###___#####________________________
__#_#_______#________________________
__###___####_________________________
_____________________________________''')
print('''__#____##__######__#######___######__
__#___#_#__#_______#___#_#__#________
__#__#__#__######__#__#__#___#####___
__#_#___#__#_______#_#___#________#__
__##____#__######__#######__######___
''')
print('''�������:
1 ���-�� ������� ����������� 
2 ���-�� *������ ����������* ''')
inp=str(input())
dopusk=1
if inp=='nestopscrt':
    dopusk=2
    print('������ �������')
elif inp=='obsolutsecretofneos':
    dopusk=3
    print('������ �������')
def load():
    for i in range(9):
        print('/',end='')
        time.sleep(0.5)
    print('/')

game_run=True
def rasshifr(txt,dpk):
    rastxt=''
    cnt=0
    cntall=0
    canprint=True
    for i in txt.split('_'):
        cntall+=1
    for i in txt.split('_'):
        cnt+=1
        if cnt<cntall:
            rastxt=rastxt+chr(int(i))
        elif cnt==cntall:
            if dpk==1 and int(i)%31!=0:
                canprint=False
            elif dpk==2 and int(i)%13!=0:
                canprint=False
            elif dpk==3 and int(i)%229!=0:
                canprint=False
    if canprint==True:
        print(rastxt)
    else:
        print('� ����������� ���������')
        print('��� ������� ������')
while game_run==True:
    if inp=='1':
        dopusk=1
        
        
        s=str(input())
        load()
        rasshifr(s,dopusk)
        
    
    
    inp=str(input())
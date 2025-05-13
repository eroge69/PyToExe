def a_rec(L,W):
    print("مساحة المستطيل =",L*W)
def a_squ(L):
    print("مساحة المربع=",L*L)
def a_circ(R):
    print("مساحة الدائرة=",3,14*R*R)

while True:
    print("تطبيق لحساب مساحة الأشكال المختلفة")
    print("*********************************")
    print("أكتب 1 لحساب مساحة الشكل المستطيل")
    print("اكتب 2 لحساب مساحة الشكل المربع")
    print("اكتب 3 لحساب مساحة الدائرة")
    choice=int(input("اكتب الرقم الذي يمثل الشكل "))
    if choice==1:
        L=float(input("أدخل طول الشكل"))
        W=float(input("أدخل عرض الشكل"))
        a_rec(L,W)
    elif choice==2:
        L=float(input("أدخل طول ضلع الشكل"))
        a_squ(L)
    elif choice==3:
        R=float(input("أدخل طول نصف قطر الدائرة"))
        a_circ(R)
    else:
        print("أختر رقم الشكل الصحيح")

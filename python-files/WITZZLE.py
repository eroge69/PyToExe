print("[A][B][C]")
print("[D][E][F]")
print("[G][H][I]")
A=int(input("A: "))
B=int(input("B: "))
C=int(input("C: "))
D=int(input("D: "))
E=int(input("E: "))
F=int(input("F: "))
G=int(input("G: "))
H=int(input("H: "))
I=int(input("I: "))
R=[A,C,D,F,G,I,A,G,B,H,C,I,A,I,G,C]
S=[B,B,E,E,H,H,D,D,E,E,F,F,E,E,E,E]
T=[C,A,F,D,I,G,G,A,H,B,I,C,I,A,C,G]
while 1==1:
  tar=int(input("Target value: "))
  i=1
  for i in range(1,16):
    if R[i]+S[i]+T[i]==tar:
      print(str(R[i])+"+"+str(S[i])+"+"+str(T[i]))
    if R[i]-S[i]+T[i]==tar:
      print(str(R[i])+"-"+str(S[i])+"+"+str(T[i]))
    if R[i]*S[i]+T[i]==tar:
      print(str(R[i])+"*"+str(S[i])+"+"+str(T[i]))
    if R[i]/S[i]+T[i]==tar:
      print(str(R[i])+"/"+str(S[i])+"+"+str(T[i]))
    if R[i]+S[i]-T[i]==tar:
      print(str(R[i])+"+"+str(S[i])+"-"+str(T[i]))
    if R[i]-S[i]-T[i]==tar:
      print(str(R[i])+"-"+str(S[i])+"-"+str(T[i]))
    if R[i]*S[i]-T[i]==tar:
      print(str(R[i])+"*"+str(S[i])+"-"+str(T[i]))
    if R[i]/S[i]-T[i]==tar:
      print(str(R[i])+"/"+str(S[i])+"-"+str(T[i]))
    if R[i]+S[i]*T[i]==tar:
      print(str(R[i])+"+"+str(S[i])+"*"+str(T[i]))
    if R[i]-S[i]*T[i]==tar:
      print(str(R[i])+"-"+str(S[i])+"*"+str(T[i]))
    if R[i]*S[i]*T[i]==tar:
      print(str(R[i])+"*"+str(S[i])+"*"+str(T[i]))
    if R[i]/S[i]*T[i]==tar:
      print(str(R[i])+"/"+str(S[i])+"*"+str(T[i]))
    if R[i]+S[i]/T[i]==tar:
      print(str(R[i])+"+"+str(S[i])+"/"+str(T[i]))
    if R[i]-S[i]/T[i]==tar:
      print(str(R[i])+"-"+str(S[i])+"/"+str(T[i]))
    if R[i]*S[i]/T[i]==tar:
      print(str(R[i])+"*"+str(S[i])+"/"+str(T[i]))
    if R[i]/S[i]/T[i]==tar:
      print(str(R[i])+"/"+str(S[i])+"/"+str(T[i]))
    if (R[i]+S[i])*T[i]==tar:
      print("("+str(R[i])+"+"+str(S[i])+")*"+str(T[i]))
    if (R[i]-S[i])*T[i]==tar:
      print("("+str(R[i])+"-"+str(S[i])+")*"+str(T[i]))
    if (R[i]+S[i])/T[i]==tar:
      print("("+str(R[i])+"+"+str(S[i])+")/"+str(T[i]))
    if (R[i]-S[i])/T[i]==tar:
      print("("+str(R[i])+"-"+str(S[i])+")/"+str(T[i]))
    if R[i]*(S[i]+T[i])==tar:
      print(str(R[i])+"*("+str(S[i])+"+"+str(T[i])+")")
    if R[i]/(S[i]+T[i])==tar:
      print(str(R[i])+"/("+str(S[i])+"+"+str(T[i])+")")
    if R[i]*(S[i]-T[i])==tar:
      print(str(R[i])+"*("+str(S[i])+"-"+str(T[i])+")")
    if S[i]-T[i]!=0:
      if R[i]/(S[i]-T[i])==tar:
        print(str(R[i])+"/("+str(S[i])+"-"+str(T[i])+")")
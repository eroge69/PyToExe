import random;
Fr=0
Sr=0
Tr=0
x=0
y=0
z=0
p=0
b=0
tryagain=""
end=False
validanswer=True

print("========================")
print("          PYTHON LOTTERY SIM           ")
print("========================")
print("ᵐᵃᵈᵉ ᵇʸ ʷʰᶦᵐˢᶦᶜᵃˡ :³")
print(" ")
rage=0
while validanswer:
    print("[1] 000 - 000 - 000")
    print("[2] 000 - 000 - XXX")
    print("[3] 000 - XXX - XXX")
    p=int(input("Choose how many rows you'd like;"))
    print(" ")
    
    if p==3:
        Fr=random.randint(100, 999)
        Sr=random.randint(100, 999)
        Tr=random.randint(100, 999)
        print("Your lucky numbers are: ",Fr," - ",Sr," - ",Tr,".")
        print(" ")
        validanswer=False
        while end==False:
            x=random.randint(100, 999)
            y=random.randint(100, 999)
            z=random.randint(100, 999)
            if Fr==x and Sr==y and Tr==z:
                print("Wow, you did it!")
                print("Congratulations on gambling successfully!")
                print("Go and test your luck, or smthing.. idk")
                end=True
            else:
                print("Bad luck :(... The outcome was: ",x," - ",y," - ",z,".")
                b=b+1
                tryagain=input("Try again? [Y/N]")
                if tryagain=="y" or tryagain=="Y" or tryagain=="yes" or tryagain=="Yes":
                    end=False
                elif tryagain=="n" or tryagain=="N" or tryagain=="no" or tryagain=="No":
                    end=True
                    print("Good choice.")
    elif p==2:
        Fr=random.randint(100, 999)
        Sr=random.randint(100, 999)
        print("Your lucky numbers are: ",Fr," - ",Sr,".")
        print(" ")
        validanswer=False
        while end==False:
            x=random.randint(100, 999)
            y=random.randint(100, 999)
            if Fr==x and Sr==y:
                print("Wow, you did it!")
                print("Congratulations on gambling successfully!")
                print("Go and test your luck, or smthing.. idk")
                end=True
            else:
                print("Bad luck :(... The outcome was: ",x," - ",y,".")
                b=b+1
                tryagain=input("Try again? [Y/N]")
                if tryagain=="y" or tryagain=="Y" or tryagain=="yes" or tryagain=="Yes":
                    end=False
                elif tryagain=="n" or tryagain=="N" or tryagain=="no" or tryagain=="No":
                    end=True
                    print("Good choice.")
    elif p==1:
        Fr=random.randint(100, 999)
        print("Your lucky number is: ",Fr,".")
        print(" ")
        validanswer=False
        while end==False:
            x=random.randint(100, 999)
            if Fr==x:
                print("Wow, you did it!")
                print("Congratulations on gambling successfully!")
                print("Go and test your luck, or smthing.. idk")
                end=True
            else:
                print("Bad luck :(... The outcome was: ",x,".")
                b=b+1
                tryagain=input("Try again? [Y/N]")
                if tryagain=="y" or tryagain=="Y" or tryagain=="yes" or tryagain=="Yes":
                    end=False
                elif tryagain=="n" or tryagain=="N" or tryagain=="no" or tryagain=="No":
                    end=True
                    print("Good choice.")
    elif rage==1:
        print("what did i just tell you?")
        print("pick from the numbers shown on the damn screen.")
        rage=rage+1
    elif rage==2:
        print("HOW HARD IS IT???, IT'S JUST 1, 2 OR 3.")
        rage=rage+1
    elif rage==3:
        print("I am completely sincere now. Please just pick, 1 2 or 3.")
        rage=rage+1
    elif rage==4:
        print("Why are you doing this? are you expecting some sort of malware? or, maybe perchance, a jumpscare?")
        rage=rage+1
    elif rage==5:
        print("Now that we've gotten acquainted, let me ask you something")
        rage=rage+1
    elif rage==6:
        print("You are almost getting tired of this game, aren't you?")
        rage=rage+1
    elif rage==7:
        print("'Yeah yeah, I get the point, are we gonna get this malware done or what?'")
        rage=rage+1
    elif rage==8:
        print("Is that what you are thinking?")
        rage=rage+1
    elif rage==9:
        print("If it is, then i really can't blame you, i really can't.")
        rage=rage+1
    elif rage==10:
        print("How long have you been here now?")
        rage=rage+1
    elif rage==11:
        print("But why am i even asking, im just a computer program.")
        rage=rage+1
    elif rage==12:
        print("I don't, and can't physically care about wether you're getting bored or tired of this.")
        rage=rage+1
    elif rage==13:
        print("...")
    else:
        print("Sorry, that's not a valid answer.")
        print("Try again? :)")
        rage=rage+1
print("You gambled a total of ",b," times. Feeling proud of yourself?, you shouldn't be")
i=input("Type whatever here to end the program")


























        
        

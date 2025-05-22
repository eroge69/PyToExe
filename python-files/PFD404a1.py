#Zheng Yu
# AEU3001517
#define score_validation
x="Math:      "
y="English:   "
z="Science:   "
def validate_score (score,message):
    while True:
        try:
            if 0<=float(score)<=100:
                break
            else:
                score = float(input(f"{message}"))
        except ValueError:
            score = float(input(f"{message}"))
    return score
#define score grade
def object_grade(score):
    if float(score) >=90:
        grade="A"
    elif float(score)>=80:
        grade="B"
    elif float(score)>=70:
        grade="C"
    elif float(score)>=60:
        grade="D"
    else:
        grade="F"
    return grade



#use while for the continuity function
while True:
    print("welcome the learner report card programme")
#input learner details
    learner_name = str(input("Learner name "))
    print("please enter validate score between 0-100")
    math_score = input("Math:      ")
    math_score=validate_score(math_score,x)
    english_score = input("English:   ")
    english_score = validate_score(english_score,y)
    science_score = input("Science:   ")
    science_score = validate_score(science_score,z)
    math_grade=object_grade(math_score)
    english_grade=object_grade(english_score)
    science_grade=object_grade(science_score)
    ave_score=round((float(math_score)+float(english_score)+float(science_score))/3,2)
    print("Report Card")
    print(f'Learner Name:  {learner_name}')
    print(f'Math:       {math_grade}')
    print(f'English:    {english_grade}')
    print(f'Science::   {science_grade}')
    print(f'Average:    {ave_score} \n     ')

    is_continue=input("Do you want to continue? (Y/N):").lower()
    if is_continue =="n":
        print("Thanks for using programme, Bye Bye")
        break
    elif is_continue!="y":
        print ("Wrong choice, continue the programme")
        continue





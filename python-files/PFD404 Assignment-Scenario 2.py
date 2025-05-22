#Zheng Yu
# AEU3001517


#assign grade

def grade_assign(score):
    if 90<=float(score)<=100:
        return "A"
    elif 80<=float(score)<90:
        return "B"
    elif 70<=float(score)<80:
        return "C"
    elif 60<=float(score)<70:
        return "D"
    else:
        return "F"
#import text file
def impo_fil():
    import os
    file_report=input("Please input the text file name")
    a=os.path.isfile(file_report)
    while True:
        if a:
            break
        else:
            file_report = input("Please input the exist text file name")
            a = os.path.isfile(file_report)
    return file_report

#import a text file
learner_score=impo_fil()

#define variable learner report and grade count
learner_report=[]
count_grade = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

#split each learner's report from the import file
with open (learner_score,'r') as f:
    for line in f:
        score_record=line.strip().split(',')
        id_name=score_record[0].strip().split(' ',2)
        id=id_name[1].strip()
        name=id_name[2].strip()
        mid_score=float(score_record[1].strip())
        end_score = float(score_record[2].strip())
        final_score=round((mid_score+end_score)/2,2)
        grade=grade_assign(final_score)
        count_grade[grade]+=1
        learner_report.append({'id':id,'name':name,'mid_score':mid_score,'end_score':end_score,'final_score':final_score,'grade':grade})
print(f"Subject: Mathematics")
print("\n{:<15} {:<18} {:<15} {:<15} {:<15} {:<10}".format(
"Learner ID", "Name", "Mid-term", "End-of-term", "Final Score", "Grade"))
print('-'*90)

for learner in learner_report:
    print("{:<15} {:<18} {:<15} {:<15} {:<15} {:<10}".format(
    learner['id'], learner['name'], learner['mid_score'], learner['end_score'], learner['final_score'],
    learner['grade']))

#print total count for each grade
print("\nTotal Count for Each Grade:")
for grade in ['A','B','C','D','F']:
    print(f'{grade}:   {count_grade[grade]}')




















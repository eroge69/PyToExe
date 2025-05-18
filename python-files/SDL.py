


from tkinter import *
from pathlib import Path
import time
import json 
path = Path('tasks.json')
def usernames():
      return input("Username : ") 

def interface(name):
    print("===Should-Do-List===")
    print(f"Hello {name.upper()} and welcome to SDL ")
    print("1 - Your tasks")
    print("2 -  DO a task")
    print("3 - Add task")
    return input("Select what you want to do by writing the number of the action here : ")

def task_doing (task_do):
      showtask(task_do)
      tasknum= int(input("Enter the number of the task you want to do now : "))
      task_list = list(task_do.items())
      if 1<= tasknum <= len(task_do):
          taskname,tasktime = task_list[tasknum -1]
          total_seconds = tasktime * 60 
          while total_seconds > 0:
              mins, secs = divmod(total_seconds,60)
              timer = '{:02d}:{:02d}'.format(mins,secs)
              print(timer,end="\r")
              time.sleep(1)
              total_seconds -= 1
          print("your time is up !!!!!!!!")
          
          
def showtask(tasks_representing):
      if not tasks_representing :
            print("\nyour list is empity\n")
      else:
            for i,(task,time) in enumerate(tasks_representing.items() ,start=1):
                  print(f"\n{i}.{task} (time:{time})\n")       
"""for i in range(len(commands)) :
            print(f"{i+1} - {commands}")"""

"""(you can use it also)"""   

def commands(task_moding):
        tsk = input("Enter the new task here : ")
        tsktime = int(input("Enter the time of the task : "))

        task_moding[tsk] = tsktime
        with open('./tasks.json', 'w') as output :
            json.dump(task_moding, output)
        
        print(f"The task ({task_moding}) entered scuccecfuly ")
        
def completetasks(task_completing):
      showtask(task_completing)
      if task_completing:
            try: 
                
                tr = int(input("Enter the number of the task you want to remove: "))
                task_list = list(task_completing.items())
                if 1<= tr <= len(task_completing):
                    taskname,tasktime = task_list[tr -1]
                    total_seconds = tasktime * 60 
                    while total_seconds > 0:
                         mins, secs = divmod(total_seconds,60)
                         timer = '{:02d}:{:02d}'.format(mins,secs)
                         print(timer,end="\r")
                         time.sleep(1)
                         total_seconds -= 1
                    print("your time is up ! you shall completed your task.")
                    del task_completing[taskname]
                    with open('./tasks.json', 'w') as output:
                       json.dump(task_completing, output, indent=2)  

                    
                else:
                  print("please enter valid number !")
            except ValueError:
                 print("Please enter valid number")
                 
                  
      else :
            print("you don't have any tasks to complete")

def main():
      username = usernames()
      tasks ={}
      if path.exists():
        content = path.read_text()
        try:
            tasks = json.loads(content)
        except json.JSONDecodeError:
            tasks = {}
      
      while True:
        choice = interface(username)
        if choice == "1":
          showtask(tasks)
        elif choice == "2":
          completetasks(tasks)
        elif choice == "3":
          commands(tasks)
        elif choice == "4" :
            task_doing(tasks)
        else:
          print("please enter valid number")
          interface(username)
if __name__ == "__main__":
    main()



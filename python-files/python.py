def load_tasks(filename="tasks.txt"):
    try:
        with open(filename, "r") as f:
            tasks = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        tasks = []
    return tasks

def save_tasks(tasks, filename="tasks.txt"):
    with open(filename, "w") as f:
        for task in tasks:
            f.write(task + "\n")

def show_tasks(tasks):
    if not tasks:
        print("No tasks found.")
    else:
        print("Your Tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

def add_task(tasks):
    task = input("Enter a new task: ").strip()
    if task:
        tasks.append(task)
        print(f"Added task: {task}")
    else:
        print("Task cannot be empty!")

def remove_task(tasks):
    show_tasks(tasks)
    if tasks:
        try:
            idx = int(input("Enter task number to remove: "))
            if 1 <= idx <= len(tasks):
                removed = tasks.pop(idx - 1)
                print(f"Removed task: {removed}")
            else:
                print("Invalid task number.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    tasks = load_tasks()
    
    while True:
        print("\nOptions:")
        print("1. Show tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Save and Exit")
        
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            remove_task(tasks)
        elif choice == "4":
            save_tasks(tasks)
            print("Tasks saved. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()

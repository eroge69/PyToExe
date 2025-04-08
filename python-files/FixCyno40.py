import os

folder_path = os.getcwd() # gets the current working directory

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isdir(file_path):
            process_folder(file_path)
        elif filename.endswith('.ini'):
            with open(file_path, 'r') as f:
                s = f.read()
            s = s.replace('68416e15', '4cc92f60')
            s = s.replace('44d9d0f7', '6867e0b8')
            with open(file_path, 'w') as f:
                f.write(s)

process_folder(folder_path)
print('done')
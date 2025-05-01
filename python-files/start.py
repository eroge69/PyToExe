def start_copy_maker(i,read_file):
    myfile = open(f"names {i + 1}.txt","a")
    myfile.write(read_file)
    myfile.close()


if __name__ == "__main__":
    read_file = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

"""
    # myfile = open("names.txt","r")
    # read_file = myfile.read()
    i = 0
    while True:
        start_copy_maker(i,read_file)
        i += 1

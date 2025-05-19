while True:
    lines = []
       
    with open('timing_data.csv', 'r') as f:
       lines = f.readlines()

    with open('timing_data_2.csv', 'w') as f:
        f.writelines(lines[:1] + lines[2:])
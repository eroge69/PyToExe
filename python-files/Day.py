# Program that takes in a day of the month
# Returns which day's Guitar Practice Routine to follow (1, 2, or 3)

def getGPday(dayOfMonth):
    if ((dayOfMonth % 3) == 0):
        return 3
    elif ((dayOfMonth % 3) == 1):
        return 1
    else:
        return 2
    
# Main program begins here:

userDate = int(input('Enter the date of the month: '))
print(f'Today, follow guitar practice routine #{getGPday(userDate)}.')
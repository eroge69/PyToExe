user_input = input()
result = []
lines = user_input.split(" @")
for line in lines:
  num = int(line[(line.find("<") + 3) : (line.find(">") - 3) ])
  result.append(line.replace(str(num), str(num + 604800)))

result[-1] = result[-1][:-48]
result.append("-# *Указывается время вашего часового пояса")

for line in result: print(line)
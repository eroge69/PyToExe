outs = int(input('Кол-во аутов: '))
street = str(input('Улица (t/r): '))
if street == "t":
 chance = (outs/47 + outs/46) * 100
 print ('эквити = ', chance, '%')
if street == "r":
 chance = (outs/46) * 100
 print ('эквити = ', chance, '%')

call = int(input('ставка для кола = ')) 
bank = int(input('банк = '))

bankchance = (call/(call+bank))*100
print ('шанс банка = ', bankchance, '%')

if chance > bankchance:
 print ('call')
else:
 print ('pass')

 
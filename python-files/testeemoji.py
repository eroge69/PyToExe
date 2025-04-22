import emoji
from emoji import *
import random
#from distutils.core import setup
#import py2exe
#setup(console=['testeemoji.py'])

print(emoji.emojize(':panda:'),'BEM VINDO AO JOGO JOKENPÔ - ESCOLHA ENTRE AS OPÇÕES ABAIXO:', emoji.emojize(':panda:'))
print('[1] - Pedra', emoji.emojize(':raised_fist:') )
print('[2] - Papel', emoji.emojize(':hand_with_fingers_splayed:'))
print('[3] - Tesoura',emoji.emojize(':victory_hand:'))


pedra = emoji.emojize(':raised_fist:')
papel = emoji.emojize(':hand_with_fingers_splayed:')
tesoura = emoji.emojize(':victory_hand:')


user = str(input('Escolha entre Pedra {} Papel{} ou Tesoura: {} \n'.format(pedra, papel, tesoura)))
pc = ['Pedra', pedra, 'Papel',papel, 'Tesoura', tesoura]

escolhapc = random.choice(pc)


if user =='Pedra':
  user = pedra
elif user =='Papel':
  user = papel
else:
  user = tesoura

if escolhapc =='Pedra':
  escolhapc = pedra
elif escolhapc =='Papel':
  escolhapc = papel
else:
  escolhapc = tesoura


print('Usuário = ', user, 'PC = ', escolhapc,'\n')

if user == pedra and escolhapc ==tesoura or user ==tesoura and escolhapc == papel or user ==papel and escolhapc==pedra:
  print('USUÁRIO Ganhou! O usuário escolheu: {} e o pc escolheu: {}'.format(user, escolhapc))
elif escolhapc == pedra and user ==tesoura or escolhapc ==tesoura and user == papel or escolhapc ==papel and user==pedra:
  print('PC Ganhou O usuário escolheu: {} e o pc escolheu: {}'.format(user, escolhapc))
else:
  print('Empate! O usuário escolheu: {} e o pc escolheu: {}'.format(user, escolhapc))


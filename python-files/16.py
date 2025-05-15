time_markers = {
    'present_simple': ['always', 'usually', 'often', 'sometimes', 'rarely', 'never', 'every day', 'on mondays'],
    'present_continuous': ['now', 'at the moment', 'right now', 'currently', 'at present'],
    'past_simple': ['yesterday', 'last night', 'last week', 'last year', 'in 1990', 'ago'],
    'past_continuous': ['while', 'when', 'as'],
    'present_perfect': ['just', 'already', 'yet', 'ever', 'never', 'since', 'for', 'so far', 'recently', 'lately'],
    'past_perfect': ['by the time', 'before', 'after'],
    'future_simple': ['tomorrow', 'soon', 'next week', 'next year', 'in the future']
}

irregular = {
    'be': ('was', 'been'),
    'become': ('became', 'become'),
    'begin': ('began', 'begun'),
    'bite': ('bit', 'bitten'),
    'blow': ('blew', 'blown'),
    'break': ('broke', 'broken'),
    'bring': ('brought', 'brought'),
    'build': ('built', 'built'),
    'buy': ('bought', 'bought'),
    'catch': ('caught', 'caught'),
    'choose': ('chose', 'chosen'),
    'come': ('came', 'come'),
    'cost': ('cost', 'cost'),
    'cut': ('cut', 'cut'),
    'do': ('did', 'done'),
    'draw': ('drew', 'drawn'),
    'drink': ('drank', 'drunk'),
    'drive': ('drove', 'driven'),
    'eat': ('ate', 'eaten'),
    'fall': ('fell', 'fallen'),
    'feed': ('fed', 'fed'),
    'feel': ('felt', 'felt'),
    'fight': ('fought', 'fought'),
    'find': ('found', 'found'),
    'fly': ('flew', 'flown'),
    'forget': ('forgot', 'forgotten'),
    'forgive': ('forgave', 'forgiven'),
    'freeze': ('froze', 'frozen'),
    'get': ('got', 'gotten'),
    'give': ('gave', 'given'),
    'go': ('went', 'gone'),
    'grow': ('grew', 'grown'),
    'hang': ('hung', 'hung'),
    'have': ('had', 'had'),
    'hear': ('heard', 'heard'),
    'hide': ('hid', 'hidden'),
    'hit': ('hit', 'hit'),
    'hold': ('held', 'held'),
    'hurt': ('hurt', 'hurt'),
    'keep': ('kept', 'kept'),
    'know': ('knew', 'known'),
    'lay': ('laid', 'laid'),
    'lead': ('led', 'led'),
    'leave': ('left', 'left'),
    'lend': ('lent', 'lent'),
    'let': ('let', 'let'),
    'lose': ('lost', 'lost'),
    'make': ('made', 'made'),
    'mean': ('meant', 'meant'),
    'meet': ('met', 'met'),
    'pay': ('paid', 'paid'),
    'put': ('put', 'put'),
    'read': ('read', 'read'),
    'ride': ('rode', 'ridden'),
    'ring': ('rang', 'rung'),
    'rise': ('rose', 'risen'),
    'run': ('ran', 'run'),
    'say': ('said', 'said'),
    'see': ('saw', 'seen'),
    'sell': ('sold', 'sold'),
    'send': ('sent', 'sent'),
    'set': ('set', 'set'),
    'shake': ('shook', 'shaken'),
    'shine': ('shone', 'shone'),
    'shoot': ('shot', 'shot'),
    'show': ('showed', 'shown'),
    'shut': ('shut', 'shut'),
    'sing': ('sang', 'sung'),
    'sit': ('sat', 'sat'),
    'sleep': ('slept', 'slept'),
    'speak': ('spoke', 'spoken'),
    'spend': ('spent', 'spent'),
    'stand': ('stood', 'stood'),
    'steal': ('stole', 'stolen'),
    'swim': ('swam', 'swum'),
    'take': ('took', 'taken'),
    'teach': ('taught', 'taught'),
    'tell': ('told', 'told'),
    'think': ('thought', 'thought'),
    'throw': ('threw', 'thrown'),
    'understand': ('understood', 'understood'),
    'wake': ('woke', 'woken'),
    'wear': ('wore', 'worn'),
    'win': ('won', 'won'),
    'write': ('wrote', 'written')
}
s = input().lower().split()
input_text = ' '.join(s)
#Проверка: маркеры времени?
for tense, markers in time_markers.items():
    for phrase in markers:
        if phrase in input_text:
            print(tense.replace('_', ' ').title())
            exit()

# Проверка подлежащего
if len(s) < 2 or s[0] not in ['i', 'you', 'he', 'she', 'it', 'we', 'they']:
    print("Incorrect sentence")
# Present Continuous или Present Simple
elif s[1] in ['am', 'is', 'are']:
    print("Present continuous" if len(s) > 2 and s[2].endswith('ing') else "Present simple")
# Past Continuous или Past Simple
elif s[1] in ['was', 'were']:
    if len(s) > 2 and s[2].endswith('ing'):
        print("Past continuous")
    elif len(s) > 2:
        v = s[2]
        if v.endswith('ed') or any(v == forms[0] for forms in irregular.values()):
            print("Past simple")
        else:
            print("Incorrect sentence")
    else:
        print("Incorrect sentence")
# Present Perfect
elif s[1] in ['have', 'has']:
    v = s[2] if len(s) > 2 else ''
    if v.endswith('ed') or any(v == forms[1] for forms in irregular.values()):
        print("Present perfect")
    else:
        print("Incorrect sentence")
# Past Perfect
elif s[1] == 'had':
    v = s[2] if len(s) > 2 else ''
    if v.endswith('ed') or any(v == forms[1] for forms in irregular.values()):
        print("Past perfect")
    else:
        print("Incorrect sentence")
# Future Simple
elif s[1] == 'will':
    if len(s) > 2 and s[2] == 'be':
        print("Future simple")
    else:
        print("Incorrect sentence")
# Простое прошедшее
elif len(s) >= 2:
    v = s[1]
    if v.endswith('ed') or any(v == forms[0] for forms in irregular.values()):
        print("Past simple")
    else:
        print("Present simple")
# Все прочие случаи — ошибка
else:
    print("Incorrect sentence")

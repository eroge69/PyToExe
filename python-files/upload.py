import telethon
from telethon import TelegramClient
import socks
from io import BytesIO
import os
import pickle
import sys

api_id = 
api_hash = ''
dirname = 'dirname'
group_id = -34535325 # create group and get the ID


client = TelegramClient('session_id',
    api_id=api_id, api_hash=api_hash,
    # proxy=(socks.PROXY_TYPE_HTTP, 'server', 3128)
)
client.start()
ent2 = client.get_input_entity(group_id)  # chat ID in Int


lis = os.listdir(dirname)
lis.sort()

the_filename = 'listdb'

try:
	with open(the_filename, 'rb') as f:
	    uploaded_list = pickle.load(f)
except:
    uploaded_list = list()
    f = open(the_filename, 'w')
    f.close()


def callable(dded, total):
	prog = int((100*dded/total))
	sys.stdout.write("\rUploading: %d%%" % prog)
	sys.stdout.flush()
	uploaded_list.append(current_file)
	if (dded == total):
	    with open(the_filename, 'wb') as f:
	        pickle.dump(uploaded_list, f)



current_file = ""
count = 0
for l in lis:
	count = count +1
	print("\n"+str(count)+"/"+str(len(lis)))
	print(l)
	if l not in uploaded_list:
		current_file = l
		client.send_file(ent2, dirname+'/'+l, progress_callback=callable, 
			force_document=True, caption=str(count)+" of "+str(len(lis))+" "+l)
	else:
		print("Already uploaded!")



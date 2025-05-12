import customtkinter as ctk

import ollama
app = ctk.CTk(fg_color='#275994')
# ai stuff
bmodel = "mistral"
tpredict = 200
topk = 100
repitition = ctk.DoubleVar(value=1.0)
random = ctk.DoubleVar(value=0.1)
history = []
sys = "your a testing bot, you are to avoid markdown text"
history.insert(0, {"role": "system", "content": sys})
# chat func
def chat(prompt):
    if prompt.strip() == "":
        return 0
    user = ctk.CTkLabel(justify='left',width=400,master=chatview,wraplength=400, text=f'user: {prompt}', anchor='w', fg_color='#1124FB', corner_radius=10)
    user.pack(fill='x')
    history.append({'role':"user", 'content':prompt})
    res = ollama.chat(model=bmodel,options={'num_predict': 100, 'temperature':random.get(), 'top_k':repitition.get()}, messages=history)
    history.append({'role':"assistant","content":res["message"]["content"]})
    resp = ctk.CTkLabel(justify='left',width=400,master=chatview,wraplength=400, anchor='e',text=f'{res['message']['content']} :bot', fg_color='#6E7877', corner_radius=10)
    resp.pack(fill='x')
    inputt.delete(0,'end')

app.geometry('800x600')
app.title("pythonGPT 1.1a")
# tabs
tabs = ctk.CTkTabview(app,width=700,height=550, fg_color='#1F4A7D')
chattab = tabs.add('chat')
settab = tabs.add('settings')
tabs.pack()
# settab
toptpl = ctk.CTkLabel(settab, text='randomness of the ai')
toptpl.pack()
toptemp = ctk.CTkSlider(settab, from_=0.1, to=2.0, variable=random)
toptemp.pack()
repptl = ctk.CTkLabel(settab, text='how many times it gets hit for repitition')
repptl.pack()
reppt = ctk.CTkSlider(settab, from_=0.1, to=2.0, variable=repitition)
reppt.pack()
# clear history
def delh():
    history.clear()
    history.insert(0, {"role": "system", "content": sys})
    for wid in chatview.winfo_children():
        wid.destroy()

chisl = ctk.CTkLabel(settab, text='clear history')
chis = ctk.CTkButton(settab,text='clear', command=lambda: delh())
chisl.pack()
chis.pack()
# chattab
chatview = ctk.CTkScrollableFrame(chattab,width=650,height=500,corner_radius=10)
inframec = ctk.CTkFrame(master=chattab,width=650,height=28)
inputt = ctk.CTkEntry(inframec,width= 650, height=28)
sendb = ctk.CTkButton(inframec,width=70,height=28,text='send',command=lambda:chat(inputt.get()))
# chattab packing
chatview.pack(pady=10)
inputt.pack(side='right')
inframec.pack()
sendb.pack(side='left')

app.bind("<Return>", lambda event: sendb.invoke())

app.mainloop()
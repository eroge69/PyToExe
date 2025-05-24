import tkinter as tk
from tkinter import filedialog, messagebox
import random
import pygame
import os
import shutil
from PIL import Image, ImageTk

imagem_animada = None
animando = False
imagens_animacao = []
indice_imagem = 0
imagem_tk = None

def carregar_imagens_animacao():
    global imagens_animacao
    pasta_imagens = "imagens"
    imagens_animacao = []

    if not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)

    for nome_arquivo in sorted(os.listdir(pasta_imagens)):
        if nome_arquivo.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            caminho = os.path.join(pasta_imagens, nome_arquivo)
            img = Image.open(caminho).resize((256, 450))
            imagens_animacao.append(ImageTk.PhotoImage(img))

def trocar_imagem_enquanto_toca():
    global imagem_animada, indice_imagem, imagens_animacao
    if not imagens_animacao or not animando:
        return

    imagem_tk_atual = imagens_animacao[indice_imagem]
    imagem_animada.config(image=imagem_tk_atual)
    imagem_animada.image = imagem_tk_atual

    indice_imagem = (indice_imagem + 1) % len(imagens_animacao)

    if pygame.mixer.music.get_busy():
        janela.after(150, trocar_imagem_enquanto_toca)

def animar_imagem_subir():
    global imagem_animada, imagem_tk, animando
    if animando:
        return
    animando = True
    altura_img = 450

    imagem = Image.open("imagens/phasmo.png")
    imagem = imagem.resize((256, altura_img))
    imagem_tk = ImageTk.PhotoImage(imagem)

    if imagem_animada is not None:
        imagem_animada.destroy()

    imagem_animada = tk.Label(janela, image=imagem_tk, borderwidth=0)
    y = 1000

    def subir():
        nonlocal y
        if y > 1000 - altura_img:
            y -= 10
            imagem_animada.place(x=760, y=y)
            janela.after(1, subir)
        else:
            monitorar_fim_do_audio()

    subir()

def animar_imagem_descer():
    global animando
    y = imagem_animada.winfo_y()

    def descer():
        nonlocal y
        if y < 1000:
            y += 10
            imagem_animada.place(x=760, y=y)
            janela.after(1, descer)
        else:
            imagem_animada.destroy()
            animando = False

    descer()

def monitorar_fim_do_audio():
    if pygame.mixer.music.get_busy():
        janela.after(500, monitorar_fim_do_audio)
    else:
        animar_imagem_descer()

# Inicializa o mixer do pygame
pygame.mixer.init()

PASTA_AUDIOS = "audios"
EXTENSOES_SUPORTADAS = (".mp3", ".wav", ".ogg", ".flac")
lista_audios = []

def carregar_audios_da_pasta():
    if not os.path.exists(PASTA_AUDIOS):
        os.makedirs(PASTA_AUDIOS)
    lista_audios.clear()
    for arquivo in os.listdir(PASTA_AUDIOS):
        if arquivo.lower().endswith(EXTENSOES_SUPORTADAS):
            caminho = os.path.join(PASTA_AUDIOS, arquivo)
            lista_audios.append(caminho)

def adicionar_audio():
    arquivos = filedialog.askopenfilenames(
        title="Selecionar arquivos de áudio",
        filetypes=[("Arquivos de Áudio", "*.mp3 *.wav *.ogg *.flac")]
    )
    if arquivos:
        for caminho_original in arquivos:
            nome_arquivo = os.path.basename(caminho_original)
            destino = os.path.join(PASTA_AUDIOS, nome_arquivo)
            if not os.path.exists(destino):
                shutil.copy2(caminho_original, destino)
        carregar_audios_da_pasta()
        messagebox.showinfo("Sucesso", "Áudios adicionados com sucesso!")

def tocar_audio(caminho):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.play()

def deletar_audio_por_nome(nome_arquivo):
    caminho = os.path.join(PASTA_AUDIOS, nome_arquivo)
    if os.path.exists(caminho):
        os.remove(caminho)
        carregar_audios_da_pasta()
        return True
    return False

def abrir_janela_audios():
    janela_audios = tk.Toplevel(janela)
    janela_audios.title("Lista de Áudios")
    janela_audios.geometry("400x300")
    janela_audios.configure(bg="lightgray")

    listbox = tk.Listbox(janela_audios, font=("Arial", 12))
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for caminho in lista_audios:
        listbox.insert(tk.END, os.path.basename(caminho))

    def ao_duplo_clique(event):
        selecao = listbox.curselection()
        if selecao:
            index = selecao[0]
            nome = listbox.get(index)
            caminho = os.path.join(PASTA_AUDIOS, nome)
            tocar_audio(caminho)

    def ao_tecla_apertada(event):
        if event.keysym == "Delete":
            selecao = listbox.curselection()
            if selecao:
                index = selecao[0]
                nome = listbox.get(index)
                if deletar_audio_por_nome(nome):
                    listbox.delete(index)
                    messagebox.showinfo("Removido", f"{nome} foi deletado.")

    listbox.bind("<Double-Button-1>", ao_duplo_clique)
    listbox.bind("<Key>", ao_tecla_apertada)

def iniciar_timer():
    global tempo_restante, timer_ativo
    try:
        minutos = int(entry_minutos.get())
        segundos = int(entry_segundos.get())
        tempo_restante = minutos * 60 + segundos
        if tempo_restante <= 0:
            raise ValueError
        timer_ativo = True
        atualizar_timer()
    except ValueError:
        messagebox.showerror("Erro", "Digite um tempo válido.")

def atualizar_timer():
    global tempo_restante, timer_ativo
    if tempo_restante > 0 and timer_ativo:
        minutos = tempo_restante // 60
        segundos = tempo_restante % 60
        label_timer.config(text=f"{minutos:02d}:{segundos:02d}")
        tempo_restante -= 1
        janela.after(1000, atualizar_timer)
    elif tempo_restante == 0 and timer_ativo:
        label_timer.config(text="00:00")
        tocar_vineboom_antes()
        timer_ativo = False

def tocar_audio_aleatorio():
    if lista_audios:
        caminho = random.choice(lista_audios)
        tocar_audio(caminho)
        carregar_imagens_animacao()
        trocar_imagem_enquanto_toca()
    else:
        messagebox.showinfo("Nenhum áudio", "Nenhum áudio foi adicionado ainda.")

def tocar_vineboom_antes():
    vineboom_path = os.path.join("vineboom", "vine-boom.mp3")
    if os.path.exists(vineboom_path):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.load(vineboom_path)
        pygame.mixer.music.play()
        animar_imagem_subir()
        janela.after(500, monitorar_fim_vineboom)
    else:
        tocar_audio_aleatorio()

def monitorar_fim_vineboom():
    if pygame.mixer.music.get_busy():
        janela.after(1, monitorar_fim_vineboom)
    else:
        tocar_audio_aleatorio()

# Interface principal
janela = tk.Tk()
janela.title("Timer com Áudio")
janela.geometry("1920x1080")
janela.configure(bg="green")

frame_botoes = tk.Frame(janela, bg="green")
frame_botoes.pack(pady=10)

btn_add = tk.Button(frame_botoes, text="Adicionar Áudio", command=adicionar_audio,
                    font=("Arial", 12), bg="white")
btn_add.grid(row=0, column=0, padx=5)

btn_ver = tk.Button(frame_botoes, text="Ver Áudios", command=abrir_janela_audios,
                    font=("Arial", 12), bg="white")
btn_ver.grid(row=0, column=1, padx=5)

frame_inputs = tk.Frame(janela, bg="green")
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="Minutos:", bg="green", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=5)
entry_minutos = tk.Entry(frame_inputs, width=5, font=("Arial", 12))
entry_minutos.grid(row=0, column=1, padx=5)

tk.Label(frame_inputs, text="Segundos:", bg="green", fg="white", font=("Arial", 12)).grid(row=0, column=2, padx=5)
entry_segundos = tk.Entry(frame_inputs, width=5, font=("Arial", 12))
entry_segundos.grid(row=0, column=3, padx=5)

btn_timer = tk.Button(janela, text="Iniciar Timer", command=iniciar_timer,
                      font=("Arial", 14), bg="white")
btn_timer.pack(pady=10)

label_timer = tk.Label(janela, text="00:00", font=("Arial", 40), bg="green", fg="white")
label_timer.pack(pady=20)

tempo_restante = 0
timer_ativo = False
carregar_audios_da_pasta()

janela.mainloop()

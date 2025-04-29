import json
import time
import threading
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
from pynput.keyboard import Key, Controller as KeyboardController
import tkinter as tk
from tkinter import messagebox

class MouseActionRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Gravador de Ações do Mouse")
        
        # Variáveis de controle
        self.recording = False
        self.playing = False
        self.paused = False
        self.actions = []
        self.current_action_index = 0
        self.loop_interval = 1.0  # Valor padrão
        self.should_stop = False
        
        # Controladores
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Configuração da interface
        self.setup_ui()
        
        # Listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack()
        
        # Botão Gravar
        self.record_button = tk.Button(
            main_frame, text="Gravar", command=self.toggle_recording,
            bg="red", fg="white", font=('Arial', 10, 'bold')
        )
        self.record_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Botão Pausar
        self.pause_button = tk.Button(
            main_frame, text="Pausar", command=self.toggle_pause,
            state=tk.DISABLED, bg="yellow", font=('Arial', 10)
        )
        self.pause_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Botão Reproduzir
        self.play_button = tk.Button(
            main_frame, text="Reproduzir", command=self.play_actions,
            bg="green", fg="white", font=('Arial', 10, 'bold')
        )
        self.play_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Botão Parar Reprodução
        self.stop_button = tk.Button(
            main_frame, text="Parar Reprodução", command=self.stop_playing,
            state=tk.DISABLED, bg="orange", font=('Arial', 10)
        )
        self.stop_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Botão Fechar
        self.close_button = tk.Button(
            main_frame, text="Fechar", command=self.close_app,
            bg="gray", fg="white", font=('Arial', 10)
        )
        self.close_button.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        
        # Configuração do loop
        loop_frame = tk.LabelFrame(main_frame, text="Configuração de Loop", padx=5, pady=5)
        loop_frame.grid(row=1, column=0, columnspan=5, pady=10, sticky="ew")
        
        tk.Label(loop_frame, text="Intervalo entre loops (segundos):").pack(side=tk.LEFT)
        
        self.loop_interval_entry = tk.Entry(loop_frame, width=10)
        self.loop_interval_entry.insert(0, "1.0")
        self.loop_interval_entry.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=2, column=0, columnspan=5, sticky="ew", pady=5)
        
        # Ações gravadas
        self.actions_text = tk.Text(main_frame, height=10, width=60, state=tk.DISABLED)
        self.actions_text.grid(row=3, column=0, columnspan=5, pady=5)
        
        # Configurar colunas para expansão
        for i in range(5):
            main_frame.columnconfigure(i, weight=1)
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.recording = True
        self.actions = []
        self.record_button.config(text="Parar Gravação", bg="darkred")
        self.pause_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.DISABLED)
        self.status_var.set("Gravando...")
        
        # Iniciar listeners
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )
        self.mouse_listener.start()
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press
        )
        self.keyboard_listener.start()
        
        # Registrar tempo inicial
        self.start_time = time.time()
    
    def stop_recording(self):
        self.recording = False
        self.record_button.config(text="Gravar", bg="red")
        self.pause_button.config(state=tk.DISABLED, text="Pausar")
        self.play_button.config(state=tk.NORMAL)
        self.status_var.set("Gravação concluída - {} ações registradas".format(len(self.actions)))
        
        # Parar listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Atualizar visualização das ações
        self.update_actions_view()
    
    def toggle_pause(self):
        if not self.paused:
            self.pause_recording()
        else:
            self.resume_recording()
    
    def pause_recording(self):
        self.paused = True
        self.pause_button.config(text="Continuar", bg="lightgreen")
        self.status_var.set("Gravação pausada")
    
    def resume_recording(self):
        self.paused = False
        self.pause_button.config(text="Pausar", bg="yellow")
        self.status_var.set("Gravando...")
    
    def on_move(self, x, y):
        if self.recording and not self.paused:
            current_time = time.time() - self.start_time
            self.actions.append({
                'type': 'move',
                'x': x,
                'y': y,
                'time': current_time
            })
    
    def on_click(self, x, y, button, pressed):
        if self.recording and not self.paused:
            current_time = time.time() - self.start_time
            action = 'press' if pressed else 'release'
            self.actions.append({
                'type': 'click',
                'action': action,
                'button': str(button),
                'x': x,
                'y': y,
                'time': current_time
            })
    
    def on_key_press(self, key):
        # Tecla de atalho para parar a gravação (ESC)
        if key == keyboard.Key.esc and self.recording:
            self.stop_recording()
    
    def update_actions_view(self):
        self.actions_text.config(state=tk.NORMAL)
        self.actions_text.delete(1.0, tk.END)
        
        for i, action in enumerate(self.actions):
            if action['type'] == 'move':
                self.actions_text.insert(tk.END, 
                    f"{i}: Move para ({action['x']}, {action['y']}) em {action['time']:.2f}s\n")
            elif action['type'] == 'click':
                self.actions_text.insert(tk.END, 
                    f"{i}: Click {action['action']} {action['button']} em ({action['x']}, {action['y']}) em {action['time']:.2f}s\n")
        
        self.actions_text.config(state=tk.DISABLED)
    
    def play_actions(self):
        if not self.actions:
            messagebox.showwarning("Aviso", "Nenhuma ação gravada para reproduzir.")
            return
        
        try:
            self.loop_interval = float(self.loop_interval_entry.get())
            if self.loop_interval < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Intervalo de loop inválido. Use um número positivo.")
            return
        
        self.playing = True
        self.should_stop = False
        self.record_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Reproduzindo...")
        
        # Executar em uma thread separada para não travar a interface
        threading.Thread(target=self.execute_actions_loop, daemon=True).start()
    
    def execute_actions_loop(self):
        try:
            while not self.should_stop:
                self.execute_actions()
                time.sleep(self.loop_interval)
                
                if not self.actions or self.should_stop:
                    break
        finally:
            self.root.after(0, self.stop_playing)
    
    def execute_actions(self):
        if not self.actions:
            return
        
        start_time = time.time()
        last_time = 0
        
        for action in self.actions:
            if self.should_stop:
                break
            
            # Esperar o tempo correto antes de executar a ação
            elapsed = time.time() - start_time
            wait_time = action['time'] - last_time
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            last_time = action['time']
            
            # Executar a ação
            if action['type'] == 'move':
                self.mouse_controller.position = (action['x'], action['y'])
            elif action['type'] == 'click':
                button = Button.left if action['button'] == 'Button.left' else Button.right
                if action['action'] == 'press':
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
    
    def stop_playing(self):
        self.should_stop = True
        self.playing = False
        self.record_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Reprodução parada")
    
    def close_app(self):
        if self.recording:
            self.stop_recording()
        if self.playing:
            self.stop_playing()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseActionRecorder(root)
    root.mainloop()
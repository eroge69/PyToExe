import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry  # Necessário instalar: pip install tkcalendar

class ProductivityDB:
    def __init__(self, db_name='productivity.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Cria as tabelas necessárias no banco de dados"""
        # Tabela de pessoas
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT,
            data_admissao DATE
        )
        ''')
        
        # Tabela de métricas de produtividade
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS metricas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER NOT NULL,
            data DATE NOT NULL,
            produtividade_liquida REAL,
            produtividade_efetiva REAL,
            tempo_utilizacao_processo REAL,
            tempo_efetivo REAL,
            FOREIGN KEY (pessoa_id) REFERENCES pessoas (id)
        )
        ''')
        
        self.conn.commit()
    
    def add_person(self, nome, cargo, data_admissao=None):
        """Adiciona uma nova pessoa ao banco de dados"""
        if data_admissao is None:
            data_admissao = datetime.now().strftime('%Y-%m-%d')
            
        self.cursor.execute('''
        INSERT INTO pessoas (nome, cargo, data_admissao)
        VALUES (?, ?, ?)
        ''', (nome, cargo, data_admissao))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def add_metrics(self, pessoa_id, data, prod_liquida, prod_efetiva, tempo_processo, tempo_efetivo):
        """Adiciona métricas de produtividade para uma pessoa"""
        self.cursor.execute('''
        INSERT INTO metricas (pessoa_id, data, produtividade_liquida, produtividade_efetiva, 
                             tempo_utilizacao_processo, tempo_efetivo)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (pessoa_id, data, prod_liquida, prod_efetiva, tempo_processo, tempo_efetivo))
        
        self.conn.commit()
    
    def update_person(self, pessoa_id, nome=None, cargo=None):
        """Atualiza informações de uma pessoa"""
        updates = []
        params = []
        
        if nome:
            updates.append("nome = ?")
            params.append(nome)
        if cargo:
            updates.append("cargo = ?")
            params.append(cargo)
        
        if not updates:
            return False
            
        query = "UPDATE pessoas SET " + ", ".join(updates) + " WHERE id = ?"
        params.append(pessoa_id)
        
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def update_metrics(self, metrica_id, **kwargs):
        """Atualiza métricas existentes"""
        valid_fields = ['produtividade_liquida', 'produtividade_efetiva', 
                       'tempo_utilizacao_processo', 'tempo_efetivo', 'data']
        
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
            
        query = "UPDATE metricas SET " + ", ".join(updates) + " WHERE id = ?"
        params.append(metrica_id)
        
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_person_metrics(self, pessoa_id, start_date=None, end_date=None):
        """Obtém todas as métricas de uma pessoa, opcionalmente filtrando por data"""
        query = '''
        SELECT m.id, m.data, m.produtividade_liquida, m.produtividade_efetiva, 
               m.tempo_utilizacao_processo, m.tempo_efetivo
        FROM metricas m
        WHERE m.pessoa_id = ?
        '''
        params = [pessoa_id]
        
        if start_date and end_date:
            query += " AND m.data BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        elif start_date:
            query += " AND m.data >= ?"
            params.append(start_date)
        elif end_date:
            query += " AND m.data <= ?"
            params.append(end_date)
        
        query += " ORDER BY m.data"
        
        self.cursor.execute(query, params)
        columns = [desc[0] for desc in self.cursor.description]
        results = self.cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in results]
    
    def get_all_people(self):
        """Obtém todas as pessoas cadastradas"""
        self.cursor.execute('SELECT id, nome, cargo, data_admissao FROM pessoas')
        columns = [desc[0] for desc in self.cursor.description]
        results = self.cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in results]
    
    def get_person_name(self, pessoa_id):
        """Obtém o nome de uma pessoa pelo ID"""
        self.cursor.execute('SELECT nome FROM pessoas WHERE id = ?', (pessoa_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def delete_person(self, pessoa_id):
        """Remove uma pessoa e todas suas métricas"""
        self.cursor.execute('DELETE FROM metricas WHERE pessoa_id = ?', (pessoa_id,))
        self.cursor.execute('DELETE FROM pessoas WHERE id = ?', (pessoa_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_metric(self, metric_id):
        """Remove uma métrica específica"""
        self.cursor.execute('DELETE FROM metricas WHERE id = ?', (metric_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        self.conn.close()

class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Produtividade")
        self.root.geometry("1200x800")
        
        self.db = ProductivityDB()
        
        self.create_widgets()
        self.update_people_list()
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame da lista de pessoas
        self.people_frame = ttk.LabelFrame(self.main_frame, text="Pessoas Cadastradas")
        self.people_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)
        
        # Treeview para lista de pessoas
        self.people_tree = ttk.Treeview(self.people_frame, columns=('id', 'nome', 'cargo', 'admissao'), show='headings')
        self.people_tree.heading('id', text='ID')
        self.people_tree.heading('nome', text='Nome')
        self.people_tree.heading('cargo', text='Cargo')
        self.people_tree.heading('admissao', text='Admissão')
        self.people_tree.column('id', width=50)
        self.people_tree.column('nome', width=150)
        self.people_tree.column('cargo', width=150)
        self.people_tree.column('admissao', width=100)
        self.people_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame de botões para pessoas
        self.people_buttons_frame = ttk.Frame(self.people_frame)
        self.people_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_person_btn = ttk.Button(self.people_buttons_frame, text="Adicionar", command=self.add_person)
        self.add_person_btn.pack(side=tk.LEFT, padx=2)
        
        self.edit_person_btn = ttk.Button(self.people_buttons_frame, text="Editar", command=self.edit_person)
        self.edit_person_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_person_btn = ttk.Button(self.people_buttons_frame, text="Remover", command=self.delete_person)
        self.delete_person_btn.pack(side=tk.LEFT, padx=2)
        
        # Frame de métricas
        self.metrics_frame = ttk.LabelFrame(self.main_frame, text="Métricas de Produtividade")
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=5, pady=5)
        
        # Treeview para métricas
        self.metrics_tree = ttk.Treeview(self.metrics_frame, columns=('id', 'data', 'prod_liq', 'prod_efet', 'tempo_proc', 'tempo_efet'), show='headings')
        self.metrics_tree.heading('id', text='ID')
        self.metrics_tree.heading('data', text='Data')
        self.metrics_tree.heading('prod_liq', text='Prod. Líquida')
        self.metrics_tree.heading('prod_efet', text='Prod. Efetiva')
        self.metrics_tree.heading('tempo_proc', text='Tempo Processo')
        self.metrics_tree.heading('tempo_efet', text='Tempo Efetivo')
        self.metrics_tree.column('id', width=50)
        self.metrics_tree.column('data', width=100)
        self.metrics_tree.column('prod_liq', width=100)
        self.metrics_tree.column('prod_efet', width=100)
        self.metrics_tree.column('tempo_proc', width=100)
        self.metrics_tree.column('tempo_efet', width=100)
        self.metrics_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame de botões para métricas
        self.metrics_buttons_frame = ttk.Frame(self.metrics_frame)
        self.metrics_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_metric_btn = ttk.Button(self.metrics_buttons_frame, text="Adicionar Métrica", command=self.add_metric)
        self.add_metric_btn.pack(side=tk.LEFT, padx=2)
        
        self.edit_metric_btn = ttk.Button(self.metrics_buttons_frame, text="Editar Métrica", command=self.edit_metric)
        self.edit_metric_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_metric_btn = ttk.Button(self.metrics_buttons_frame, text="Remover Métrica", command=self.delete_metric)
        self.delete_metric_btn.pack(side=tk.LEFT, padx=2)
        
        self.plot_btn = ttk.Button(self.metrics_buttons_frame, text="Gerar Gráfico", command=self.plot_metrics)
        self.plot_btn.pack(side=tk.LEFT, padx=2)
        
        # Frame do gráfico
        self.plot_frame = ttk.LabelFrame(self.root, text="Gráfico de Evolução")
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas para o gráfico
        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar evento de seleção na lista de pessoas
        self.people_tree.bind('<<TreeviewSelect>>', self.on_person_select)
    
    def update_people_list(self):
        """Atualiza a lista de pessoas no Treeview"""
        for i in self.people_tree.get_children():
            self.people_tree.delete(i)
        
        people = self.db.get_all_people()
        for person in people:
            self.people_tree.insert('', tk.END, values=(
                person['id'],
                person['nome'],
                person['cargo'],
                person['data_admissao']
            ))
    
    def update_metrics_list(self, person_id):
        """Atualiza a lista de métricas para a pessoa selecionada"""
        for i in self.metrics_tree.get_children():
            self.metrics_tree.delete(i)
        
        if person_id:
            metrics = self.db.get_person_metrics(person_id)
            for metric in metrics:
                self.metrics_tree.insert('', tk.END, values=(
                    metric['id'],
                    metric['data'],
                    metric['produtividade_liquida'],
                    metric['produtividade_efetiva'],
                    metric['tempo_utilizacao_processo'],
                    metric['tempo_efetivo']
                ))
    
    def on_person_select(self, event):
        """Evento de seleção de uma pessoa na lista"""
        selected = self.people_tree.selection()
        if selected:
            person_id = self.people_tree.item(selected[0], 'values')[0]
            self.update_metrics_list(person_id)
    
    def add_person(self):
        """Adiciona uma nova pessoa"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Pessoa")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        nome_entry = ttk.Entry(dialog, width=30)
        nome_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Cargo:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        cargo_entry = ttk.Entry(dialog, width=30)
        cargo_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Data de Admissão:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        data_entry = DateEntry(dialog, width=12, background='darkblue', 
                              foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        data_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            nome = nome_entry.get()
            cargo = cargo_entry.get()
            data_adm = data_entry.get()
            
            if not nome:
                messagebox.showerror("Erro", "O nome é obrigatório!")
                return
            
            self.db.add_person(nome, cargo, data_adm)
            self.update_people_list()
            dialog.destroy()
        
        ttk.Button(dialog, text="Salvar", command=save).grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)
    
    def edit_person(self):
        """Edita uma pessoa existente"""
        selected = self.people_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma pessoa para editar!")
            return
        
        person_id = self.people_tree.item(selected[0], 'values')[0]
        person_name = self.people_tree.item(selected[0], 'values')[1]
        person_cargo = self.people_tree.item(selected[0], 'values')[2]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Pessoa")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        nome_entry = ttk.Entry(dialog, width=30)
        nome_entry.insert(0, person_name)
        nome_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Cargo:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        cargo_entry = ttk.Entry(dialog, width=30)
        cargo_entry.insert(0, person_cargo)
        cargo_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def save():
            nome = nome_entry.get()
            cargo = cargo_entry.get()
            
            if not nome:
                messagebox.showerror("Erro", "O nome é obrigatório!")
                return
            
            self.db.update_person(person_id, nome, cargo)
            self.update_people_list()
            dialog.destroy()
        
        ttk.Button(dialog, text="Salvar", command=save).grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)
    
    def delete_person(self):
        """Remove uma pessoa"""
        selected = self.people_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma pessoa para remover!")
            return
        
        person_id = self.people_tree.item(selected[0], 'values')[0]
        person_name = self.people_tree.item(selected[0], 'values')[1]
        
        if messagebox.askyesno("Confirmar", f"Remover {person_name} e todas suas métricas?"):
            self.db.delete_person(person_id)
            self.update_people_list()
            self.update_metrics_list(None)
    
    def add_metric(self):
        """Adiciona uma nova métrica"""
        selected = self.people_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma pessoa para adicionar métricas!")
            return
        
        person_id = self.people_tree.item(selected[0], 'values')[0]
        person_name = self.people_tree.item(selected[0], 'values')[1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Adicionar Métrica para {person_name}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Data:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        data_entry = DateEntry(dialog, width=12, background='darkblue', 
                             foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        data_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Produtividade Líquida:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        prod_liq_entry = ttk.Entry(dialog, width=15)
        prod_liq_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Produtividade Efetiva:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        prod_efet_entry = ttk.Entry(dialog, width=15)
        prod_efet_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Tempo em Processo:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        tempo_proc_entry = ttk.Entry(dialog, width=15)
        tempo_proc_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Tempo Efetivo:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        tempo_efet_entry = ttk.Entry(dialog, width=15)
        tempo_efet_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            try:
                data = data_entry.get()
                prod_liq = float(prod_liq_entry.get())
                prod_efet = float(prod_efet_entry.get())
                tempo_proc = float(tempo_proc_entry.get())
                tempo_efet = float(tempo_efet_entry.get())
                
                self.db.add_metrics(person_id, data, prod_liq, prod_efet, tempo_proc, tempo_efet)
                self.update_metrics_list(person_id)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos! Certifique-se de usar números.")
        
        ttk.Button(dialog, text="Salvar", command=save).grid(row=5, column=1, padx=5, pady=10, sticky=tk.E)
    
    def edit_metric(self):
        """Edita uma métrica existente"""
        selected_metric = self.metrics_tree.selection()
        if not selected_metric:
            messagebox.showwarning("Aviso", "Selecione uma métrica para editar!")
            return
        
        metric_id = self.metrics_tree.item(selected_metric[0], 'values')[0]
        metric_data = self.metrics_tree.item(selected_metric[0], 'values')[1]
        prod_liq = self.metrics_tree.item(selected_metric[0], 'values')[2]
        prod_efet = self.metrics_tree.item(selected_metric[0], 'values')[3]
        tempo_proc = self.metrics_tree.item(selected_metric[0], 'values')[4]
        tempo_efet = self.metrics_tree.item(selected_metric[0], 'values')[5]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Métrica")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Data:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        data_entry = DateEntry(dialog, width=12, background='darkblue', 
                             foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        data_entry.set_date(metric_data)
        data_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Produtividade Líquida:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        prod_liq_entry = ttk.Entry(dialog, width=15)
        prod_liq_entry.insert(0, prod_liq)
        prod_liq_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Produtividade Efetiva:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        prod_efet_entry = ttk.Entry(dialog, width=15)
        prod_efet_entry.insert(0, prod_efet)
        prod_efet_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Tempo em Processo:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        tempo_proc_entry = ttk.Entry(dialog, width=15)
        tempo_proc_entry.insert(0, tempo_proc)
        tempo_proc_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Tempo Efetivo:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        tempo_efet_entry = ttk.Entry(dialog, width=15)
        tempo_efet_entry.insert(0, tempo_efet)
        tempo_efet_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            try:
                data = data_entry.get()
                prod_liq = float(prod_liq_entry.get())
                prod_efet = float(prod_efet_entry.get())
                tempo_proc = float(tempo_proc_entry.get())
                tempo_efet = float(tempo_efet_entry.get())
                
                self.db.update_metrics(metric_id, data=data, produtividade_liquida=prod_liq,
                                     produtividade_efetiva=prod_efet, tempo_utilizacao_processo=tempo_proc,
                                     tempo_efetivo=tempo_efet)
                
                # Atualiza a lista de métricas
                selected_person = self.people_tree.selection()
                if selected_person:
                    person_id = self.people_tree.item(selected_person[0], 'values')[0]
                    self.update_metrics_list(person_id)
                
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos! Certifique-se de usar números.")
        
        ttk.Button(dialog, text="Salvar", command=save).grid(row=5, column=1, padx=5, pady=10, sticky=tk.E)
    
    def delete_metric(self):
        """Remove uma métrica"""
        selected = self.metrics_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma métrica para remover!")
            return
        
        metric_id = self.metrics_tree.item(selected[0], 'values')[0]
        
        if messagebox.askyesno("Confirmar", "Remover esta métrica?"):
            self.db.delete_metric(metric_id)
            
            # Atualiza a lista de métricas
            selected_person = self.people_tree.selection()
            if selected_person:
                person_id = self.people_tree.item(selected_person[0], 'values')[0]
                self.update_metrics_list(person_id)
    
    def plot_metrics(self):
        """Gera o gráfico de evolução semestral"""
        selected_person = self.people_tree.selection()
        if not selected_person:
            messagebox.showwarning("Aviso", "Selecione uma pessoa para gerar o gráfico!")
            return
        
        person_id = self.people_tree.item(selected_person[0], 'values')[0]
        person_name = self.people_tree.item(selected_person[0], 'values')[1]
        
        # Pergunta pelo período
        dialog = tk.Toplevel(self.root)
        dialog.title("Período do Gráfico")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Data Inicial:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        start_date_entry = DateEntry(dialog, width=12, background='darkblue', 
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Data Final:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        end_date_entry = DateEntry(dialog, width=12, background='darkblue', 
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        end_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        def generate():
            start_date = start_date_entry.get()
            end_date = end_date_entry.get()
            
            metrics = self.db.get_person_metrics(person_id, start_date, end_date)
            
            if not metrics:
                messagebox.showerror("Erro", "Nenhuma métrica encontrada para o período especificado!")
                return
            
            # Prepara os dados para o gráfico
            df = pd.DataFrame(metrics)
            df['data'] = pd.to_datetime(df['data'])
            df.set_index('data', inplace=True)
            
            # Limpa a figura anterior
            self.figure.clear()
            
            # Cria o gráfico
            axs = self.figure.subplots(2, 2)
            self.figure.suptitle(f'Evolução de Produtividade - {person_name}\n{start_date} a {end_date}', fontsize=12)
            
            # Produtividade Líquida
            axs[0, 0].plot(df.index, df['produtividade_liquida'], marker='o', color='b')
            axs[0, 0].set_title('Produtividade Líquida')
            axs[0, 0].grid(True)
            
            # Produtividade Efetiva
            axs[0, 1].plot(df.index, df['produtividade_efetiva'], marker='o', color='g')
            axs[0, 1].set_title('Produtividade Efetiva')
            axs[0, 1].grid(True)
            
            # Tempo em Processo
            axs[1, 0].plot(df.index, df['tempo_utilizacao_processo'], marker='o', color='r')
            axs[1, 0].set_title('Tempo de Utilização em Processo')
            axs[1, 0].grid(True)
            
            # Tempo Efetivo
            axs[1, 1].plot(df.index, df['tempo_efetivo'], marker='o', color='purple')
            axs[1, 1].set_title('Tempo Efetivo')
            axs[1, 1].grid(True)
            
            # Formatação dos eixos de data
            date_form = plt.matplotlib.dates.DateFormatter("%Y-%m")
            for ax in axs.flat:
                ax.xaxis.set_major_formatter(date_form)
                ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator())
                for label in ax.get_xticklabels():
                    label.set_rotation(45)
            
            self.figure.tight_layout()
            self.canvas.draw()
            dialog.destroy()
        
        ttk.Button(dialog, text="Gerar Gráfico", command=generate).grid(row=2, column=1, padx=5, pady=10, sticky=tk.E)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityApp(root)
    app.run()
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from matplotlib.backends.backend_pdf import PdfPages

# Encontrar o arquivo CSV que começa com "Pressão"
csv_files = glob.glob("Pressão*.csv")
if not csv_files:
    print("Nenhum arquivo CSV encontrado.")
    exit()

csv_file = csv_files[0]

# Ler o arquivo CSV, selecionando apenas as colunas desejadas
df = pd.read_csv(csv_file, usecols=["Data da medição", "SYS(mmHg)", "DIA(mmHg)", "Pulso(bpm)"])

# Nome do arquivo PDF
pdf_file = os.path.splitext(csv_file)[0] + ".pdf"

# Verificar se o arquivo PDF já existe e removê-lo
if os.path.exists(pdf_file):
    os.remove(pdf_file)
    print(f"Arquivo PDF existente removido: {pdf_file}")

# Criar um gráfico
plt.figure(figsize=(12, 8))  # Aumentar o tamanho da figura para evitar truncamento dos rótulos
ax = plt.gca()

# Pintar o fundo do gráfico entre 80 e 120 no eixo Y
ax.axhspan(80, 120, facecolor='aquamarine', alpha=0.5)

# Adicionar barras verticais para SYS(mmHg) e DIA(mmHg) com cor azul
for index, row in df.iterrows():
    plt.plot([row["Data da medição"], row["Data da medição"]], [row["DIA(mmHg)"], row["SYS(mmHg)"]], color='blue')

# Adicionar pontos para Pulso(bpm) com cor preta
plt.scatter(df["Data da medição"], df["Pulso(bpm)"], color='black', marker='o')

# Configurar rótulos do eixo X com tamanho de fonte 6
plt.xticks(rotation=80, fontsize=6)
plt.xlabel("Data da medição")
plt.ylabel("Valores")

# Adicionar título
plt.title("Gráfico de Pressão e Pulso - Omron HEM-6181 - Connect Omron")

# Salvar o gráfico em um arquivo PDF
with PdfPages(pdf_file) as pdf:
    pdf.savefig()

print(f"Arquivo PDF criado: {pdf_file}")

# Criar um novo arquivo PDF para a tabela
table_pdf_file = os.path.splitext(csv_file)[0] + "_tabela.pdf"
pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.add_page()
pdf.set_font("Arial", size=10)

# Adicionar título
pdf.cell(200, 10, txt="Tabela de Dados Utilizados no Gráfico", ln=True, align='C')

# Adicionar cabeçalho da tabela
pdf.cell(50, 10, txt="Data da medição", border=1)
pdf.cell(40, 10, txt="SYS(mmHg)", border=1)
pdf.cell(40, 10, txt="DIA(mmHg)", border=1)
pdf.cell(40, 10, txt="Pulso(bpm)", border=1)
pdf.ln()

# Adicionar dados da tabela
for index, row in df.iterrows():
    pdf.cell(50, 10, txt=row["Data da medição"], border=1)
    pdf.cell(40, 10, txt=str(row["SYS(mmHg)"]), border=1)
    pdf.cell(40, 10, txt=str(row["DIA(mmHg)"]), border=1)
    pdf.cell(40, 10, txt=str(row["Pulso(bpm)"]), border=1)
    pdf.ln()

# Salvar o arquivo PDF da tabela
pdf.output(table_pdf_file)
print(f"Arquivo PDF da tabela criado: {table_pdf_file}")

# Remover o arquivo CSV
os.remove(csv_file)
print(f"Arquivo CSV removido: {csv_file}")

import pandas as pd
import re

# Conteúdo do arquivo Inv_00.txt
# O conteúdo completo do arquivo Inv_00.txt foi carregado no ambiente.
# Agora, o script Python irá ler o conteúdo diretamente do arquivo carregado.

# Caminho para o arquivo .txt
caminho_txt = 'Inv_00.txt'

# Carrega o conteúdo
with open(caminho_txt, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

dados = []
grupo_estoque = ""
firma_atual = ""
unidades = ['UN', 'KG', 'M', 'PC', 'L', 'CJ']

for linha in linhas:
    linha = linha.rstrip()

    # Firma (topo de página)
    if linha.startswith("FIRMA"):
        firma_atual = linha.strip()
        continue

    # Grupo Estoque
    if linha.startswith("Grupo Estoque:"):
        grupo_estoque = linha.split("Grupo Estoque:")[1].strip()
        continue

    # Ignorar cabeçalhos e totais
    if (
        "ESTOQUES EXISTENTES" in linha or
        "FISCAL" in linha or
        "VALORES" in linha or
        "TOTAL DO" in linha or
        "SUB-TOTAL" in linha or
        linha.strip() == ""
    ):
        continue

    partes = re.split(r'\s{2,}', linha)

    if len(partes) >= 6:
        try:
            codigo_fiscal = partes[0]
            codigo_interno = partes[1]
            # Encontra o índice da unidade de forma mais robusta, procurando nas últimas partes primeiro
            unidade_index = -1
            for i in range(len(partes) - 1, -1, -1):
                if partes[i] in unidades:
                    unidade_index = i
                    break

            if unidade_index == -1: # Se não encontrou a unidade, pula a linha
                continue

            descricao = ' '.join(partes[2:unidade_index])
            unidade = partes[unidade_index]
            
            # Ajusta os índices para acessar quantidade, valor_unitario e valor_total
            # Eles devem vir logo após a unidade.
            quantidade_str = partes[unidade_index + 1]
            valor_unitario_str = partes[unidade_index + 2]
            valor_total_str = partes[unidade_index + 3]

            quantidade = float(quantidade_str.replace('.', '').replace(',', '.'))
            valor_unitario = float(valor_unitario_str.replace('.', '').replace(',', '.'))
            valor_total = float(valor_total_str.replace('.', '').replace(',', '.'))

            dados.append({
                'Firma': firma_atual,
                'Grupo Estoque': grupo_estoque,
                'Código Fiscal': codigo_fiscal,
                'Código Interno': codigo_interno,
                'Descrição': descricao,
                'Unidade': unidade,
                'Quantidade': quantidade,
                'Valor Unitário': valor_unitario,
                'Valor Total': valor_total
            })
        except (ValueError, IndexError):
            # Ignora linhas que não se encaixam no padrão esperado após a tentativa
            continue

# Exporta para Excel
df = pd.DataFrame(dados)
df.to_excel('inventario_facchini_com_firma.xlsx', index=False)

print("Processamento concluído. O arquivo 'inventario_facchini_com_firma.xlsx' foi gerado.")
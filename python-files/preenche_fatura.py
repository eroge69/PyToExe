
import pdfplumber
from docx import Document
import re

def extrair_dados_pdf(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        texto = "\n".join(page.extract_text() for page in pdf.pages)

    cliente = "Tribunal Regional do Trabalho"

    valor_fatura_match = re.search(r"TOTAL\s+(\d{1,3}(?:\.\d{3})*,\d{2})", texto)
    valor_fatura = valor_fatura_match.group(1) if valor_fatura_match else "N/D"

    data_emissao_match = re.search(r"DATA DE EMISSÃO:\s*(\d{2}/\d{2}/\d{4})", texto)
    data_emissao = data_emissao_match.group(1) if data_emissao_match else "N/D"

    bandeira_match = re.search(r"Bandeira (amarela|verde|vermelha)", texto, re.IGNORECASE)
    bandeira = bandeira_match.group(1).capitalize() if bandeira_match else "N/D"

    numero_fatura_match = re.search(r"Nota Fiscal:\s*(\d+)", texto)
    numero_fatura = numero_fatura_match.group(1) if numero_fatura_match else "N/D"

    pis_match = re.search(r"PIS/PASEP .*? (\d{1,3}(?:\.\d{3})*,\d{2})", texto)
    cofins_match = re.search(r"COFINS .*? (\d{1,3}(?:\.\d{3})*,\d{2})", texto)
    icms_match = re.search(r"ICMS\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,2},\d{2}\s+(\d{1,3}(?:\.\d{3})*,\d{2})", texto)

    def parse_valor(valor_str):
        return float(valor_str.replace(".", "").replace(",", ".")) if valor_str else 0.0

    pis = parse_valor(pis_match.group(1)) if pis_match else 0.0
    cofins = parse_valor(cofins_match.group(1)) if cofins_match else 0.0
    icms = parse_valor(icms_match.group(1)) if icms_match else 0.0
    total_impostos = pis + cofins + icms

    retencoes_matches = re.findall(r"Retenção De Tributos Federais.*?(\d{1,3}(?:\.\d{3})*,\d{2})-", texto)
    retencoes = sum(parse_valor(v) for v in retencoes_matches)

    valor_fatura_float = parse_valor(valor_fatura)
    total_com_impostos = valor_fatura_float + total_impostos
    total_com_retencao = valor_fatura_float + retencoes

    return {
        "CLIENTE": cliente,
        "VALOR_FATURA": f"R$ {valor_fatura}",
        "IMPOSTOS": f"R$ {total_impostos:,.2f}".replace(".", "#").replace(",", ".").replace("#", ","),
        "TOTAL_COM_IMPOSTOS": f"R$ {total_com_impostos:,.2f}".replace(".", "#").replace(",", ".").replace("#", ","),
        "RETENCOES": f"R$ {retencoes:,.2f}".replace(".", "#").replace(",", ".").replace("#", ","),
        "TOTAL_COM_RETENCAO": f"R$ {total_com_retencao:,.2f}".replace(".", "#").replace(",", ".").replace("#", ","),
        "DATA_EMISSAO": data_emissao,
        "BANDEIRA": bandeira,
        "NUMERO_FATURA": numero_fatura
    }

def preencher_modelo_word(dados, caminho_modelo, caminho_saida):
    doc = Document(caminho_modelo)
    for paragrafo in doc.paragraphs:
        for chave, valor in dados.items():
            paragrafo.text = paragrafo.text.replace(f"{{{{{chave}}}}}", valor)
    doc.save(caminho_saida)
    print("Documento gerado com sucesso!")

if __name__ == "__main__":
    caminho_pdf = "fatura.pdf"
    caminho_modelo = "modelo.docx"
    caminho_saida = "fatura_preenchida.docx"

    dados_extraidos = extrair_dados_pdf(caminho_pdf)
    preencher_modelo_word(dados_extraidos, caminho_modelo, caminho_saida)

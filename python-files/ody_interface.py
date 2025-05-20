#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
from datetime import datetime

PASSWORD = "2237"

def main():
    # Moldura e prompt
    print("┌" + "─"*45 + "┐")
    print("│   INTERFACE DE SISTEMA - IA: ODY".ljust(46) + "│")
    print("│   CLASSIFICAÇÃO: NÍVEL 3".ljust(46) + "│")
    print("│  INSIRA O CÓDIGO DE SEGURANÇA [____]".ljust(46) + "│")
    print("└" + "─"*45 + "┘\n")

    senha = getpass.getpass(prompt="Código de segurança: ")

    if senha == PASSWORD:
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(f"\n> Acesso autorizado: {now}\n")

        print(
            ">> LOG AUTOMÁTICO - 2084/03/12\n"
            ">> 03:02 – Pico de energia nos reatores secundários.\n"
            ">> 03:08 – Porta do ambiente interno eletrico destravada manualmente.\n"
            ">> 03:12 – Circuito de biossegurança desativado no nível 1.\n"
            ">> 03:14 – Trabalhando com energia reduzida\n"
            ">> 03:15 – Reduzindo níveis de energia para todos os setores.\n"
            ">> 03:26 – Problemas detectados em na parte eletrica, gravitacional e ventilação.\n"
            ">> 03:39 – Alarme de quarentena silenciado. Iniciando em 30 Minutos.\n"
            ">> 03:53 – Setor Botanico registra anomalia em ECG (tripulante não identificado).\n"
            ">> 04:06 – Comando externo tenta encaminhar logs e arquivos para fora. (falha).\n"
            ">> 04:11 – Última leitura de intercom: “...volta aqui!” captado no corredor do nível 2.\n"
            ">> 04:13 – INICIANDO PROTOCOLO \"QUARENTENA\" EM 3...2...1...\n"
            ">> 04:15 – Desativando gravidade simulada.\n"
            ">> 04:16 – Trancando passagens, portas e níveis;\n"
            ">> 04:17 – Reativando o Alarme silencioso.\n"
            ">> 04:20 – Anomalia detectada no sistema de ventilação.\n"
            ">> 04:21 – Anomalia detectada nos ductos de ar.\n\n"
            ">> Arquivos LOG_0312 deletados manualmente.\n"
            ">> Autor identificado: [ID: H_C]"
        )
    else:
        print("\n> Acesso negado. Código incorreto.")

if __name__ == "__main__":
    main()

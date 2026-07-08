import os
import pandas as pd
import yagmail

# CONFIGURAÇÕES
PASTA_RAIZ = r"C:\Users\.....\....\.....\Notas Fiscais e Boletos"
CAMINHO_PLANILHA_EMAILS = r"C:\Users\....\......\.....\......\........\Programa Envio Emails\teste"
COL_EMPRESA = "Empresa"
COL_EMAILS = "E-mails"
COL_PASTA = "Pasta"
COL_TIPO_ENVIO = "Tipo de Envio"

# LOGIN GMAIL
SEU_EMAIL = "d......classified"
SENHA_APP = "h......classified"

# SELEÇÃO DO MÊS
mes = input("Digite o nome da pasta do mês (ex: Agosto 2025): ").strip()
pasta_mes = os.path.join(PASTA_RAIZ, mes)

if not os.path.exists(pasta_mes):
    print(f"❌ Pasta '{pasta_mes}' não encontrada.")
    exit()

df = pd.read_excel(CAMINHO_PLANILHA_EMAILS)
yag = yagmail.SMTP(SEU_EMAIL, SENHA_APP)

for idx, linha in df.iterrows():
    empresa = linha[COL_EMPRESA]
    emails = linha[COL_EMAILS]
    nome_pasta = linha[COL_PASTA]
    tipo_envio = linha[COL_TIPO_ENVIO].strip().lower()  # ambos, nf, boleto

    caminho_empresa = os.path.join(pasta_mes, nome_pasta)

    if not os.path.isdir(caminho_empresa):
        print(f"⚠️ Pasta '{nome_pasta}' não encontrada para '{empresa}'. Pulando.")
        continue

    # Busca arquivos PDF e filtra conforme o tipo de envio
    arquivos_pdf = [
        os.path.join(caminho_empresa, f)
        for f in os.listdir(caminho_empresa)
        if f.lower().endswith(".pdf")
    ]

    if not arquivos_pdf:
        print(f"⚠️ Nenhum PDF encontrado em '{nome_pasta}'.")
        continue

    anexos = []
    for arquivo in arquivos_pdf:
        nome_arquivo = os.path.basename(arquivo).lower()
        if tipo_envio == "ambos":
            anexos.append(arquivo)
        elif tipo_envio == "nf" and "NF" or "Nota Fiscal" in nome_arquivo:
            anexos.append(arquivo)
        elif tipo_envio == "boleto" and "boleto" in nome_arquivo:
            anexos.append(arquivo)

    if not anexos:
        print(f"⚠️ Nenhum anexo correspondente ao tipo '{tipo_envio}' para '{empresa}'.")
        continue

    # Revisão manualA
    print(f"\n📧 Empresa: {empresa}")
    print(f"Pasta: {nome_pasta}")
    print(f"Tipo de envio: {tipo_envio}")
    print(f"E-mails: {emails}")
    print("Anexos:")
    for a in anexos:
        print(f" - {os.path.basename(a)}")

    confirmar = input("Deseja enviar este e-mail? (s/n): ").strip().lower()
    if confirmar != "s":
        print("⏭️ E-mail não enviado.\n")
        continue

    # Envio
    if tipo_envio == "ambos":
        assunto = f"Nota Fiscal e Boleto – {empresa}"
        corpo = (
            "Prezados,\n\n"
            "Segue em anexo, nota fiscal e boleto bancário para pagamento referente a prestação de serviços.\n\n"
            "Colocamo-nos à disposição.\n\n Atenciosamente,"
        )
    elif tipo_envio == "nf":
        assunto = f"Nota Fiscal – {empresa}"
        corpo = (
            "Prezados,\n\n"
            "Segue em anexo, nota fiscal referente a prestação de serviços.\n\n"
            "Colocamo-nos à disposição.\n\n Atenciosamente,"
        )
    elif tipo_envio == "boleto":
        assunto = f"Boleto – {empresa}"
        corpo = (
            "Prezados,\n\n"
            "Segue em anexo, boleto bancário para pagamento referente a prestação de serviços.\n\n"
            "Colocamo-nos à disposição.\n\n Atenciosamente,"
        )
    else:
        print(f"❌ Tipo de envio inválido para '{empresa}'. Deve ser: ambos, NF ou boleto.")
        continue

    try:
        yag.send(to=emails, subject=assunto, contents=corpo, attachments=anexos)
        print("✅ E-mail enviado com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail para {empresa}: {e}")


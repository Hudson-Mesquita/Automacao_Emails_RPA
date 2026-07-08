import os

def buscar_anexos(caminho_empresa, tipo_envio):
    arquivos_pdf = [
        os.path.join(caminho_empresa, f)
        for f in os.listdir(caminho_empresa)
        if f.lower().endswith(".pdf")
    ]

    anexos = []

    for arquivo in arquivos_pdf:
        nome_arquivo = os.path.basename(arquivo).lower()

        if tipo_envio == "ambos":
            anexos.append(arquivo)

        elif tipo_envio == "nf" and "nf" in nome_arquivo:
            anexos.append(arquivo)

        elif tipo_envio == "boleto" and "boleto" in nome_arquivo:
            anexos.append(arquivo)

    return anexos

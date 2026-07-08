import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import pandas as pd
import yagmail
import threading

# === CONFIG INICIAIS ===
SEU_EMAIL = "d..... classified"
SENHA_APP = "h..... classified"

COL_EMPRESA = "Empresa"
COL_EMAILS = "E-mails"
COL_PASTA = "Pasta"
COL_TIPO_ENVIO = "Tipo de Envio"

CONFIG_PATH = "config.json"
config = {
    "planilha": "",
    "pasta_raiz": ""
}

df = None
pasta_mes_atual = ""

# === Funções de CONFIG ===

def salvar_config():
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def carregar_config():
    global config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

# === Funções GUI ===

def escolher_planilha():
    caminho = filedialog.askopenfilename(filetypes=[("Planilhas Excel", "*.xlsx *.xls")])
    if caminho:
        config["planilha"] = caminho
        entrada_planilha.delete(0, tk.END)
        entrada_planilha.insert(0, caminho)
        salvar_config()

def escolher_pasta_raiz():
    pasta = filedialog.askdirectory()
    if pasta:
        config["pasta_raiz"] = pasta
        entrada_pasta.delete(0, tk.END)
        entrada_pasta.insert(0, pasta)
        salvar_config()

def carregar_clientes():
    global df
    if not config["planilha"]:
        messagebox.showerror("Erro", "Selecione uma planilha válida.")
        return
    try:
        df = pd.read_excel(config["planilha"])
        lista_clientes.delete(0, tk.END)
        for idx, row in df.iterrows():
            empresa = row.get(COL_EMPRESA, "Sem nome")
            lista_clientes.insert(tk.END, f"{idx+1}. {empresa}")
        messagebox.showinfo("Sucesso", "Clientes carregados.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler planilha: {e}")

def definir_pasta_mes():
    global pasta_mes_atual
    mes = entrada_mes.get().strip()
    if not mes:
        messagebox.showerror("Erro", "Digite o nome da pasta do mês (ex: Agosto 2025)")
        return
    pasta = os.path.join(config["pasta_raiz"], mes)
    if not os.path.exists(pasta):
        messagebox.showerror("Erro", f"Pasta '{pasta}' não encontrada.")
        return
    pasta_mes_atual = pasta
    messagebox.showinfo("Pasta definida", f"Pasta do mês definida como:\n{pasta}")

def enviar_email_cliente():
    selecionado = lista_clientes.curselection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um cliente da lista.")
        return
    if not pasta_mes_atual:
        messagebox.showerror("Erro", "Defina a pasta do mês primeiro.")
        return

    idx = selecionado[0]
    linha = df.iloc[idx]
    empresa = linha[COL_EMPRESA]
    emails_raw = str(linha[COL_EMAILS])
    nome_pasta = linha[COL_PASTA]
    tipo_envio = linha[COL_TIPO_ENVIO].strip().lower()

    emails = [e.strip() for e in emails_raw.replace(";", ",").split(",") if e.strip()]
    caminho_empresa = os.path.join(pasta_mes_atual, nome_pasta)
    if not os.path.isdir(caminho_empresa):
        messagebox.showwarning("Pasta não encontrada", f"Pasta '{nome_pasta}' não existe.")
        return

    arquivos_pdf = [
        os.path.join(caminho_empresa, f)
        for f in os.listdir(caminho_empresa)
        if f.lower().endswith(".pdf")
    ]
    if not arquivos_pdf:
        messagebox.showwarning("Sem arquivos", f"Nenhum PDF encontrado para {empresa}.")
        return

    anexos = []
    for arquivo in arquivos_pdf:
        nome_arquivo = os.path.basename(arquivo).lower()
        if tipo_envio == "ambos":
            anexos.append(arquivo)
        elif tipo_envio == "nf" and "nf" in nome_arquivo:
            anexos.append(arquivo)
        elif tipo_envio == "boleto" and "boleto" in nome_arquivo:
            anexos.append(arquivo)

    if not anexos:
        messagebox.showwarning("Sem anexos", f"Nenhum PDF correspondente ao tipo '{tipo_envio}' encontrado.")
        return

    lista_arquivos = "\n".join([os.path.basename(a) for a in anexos])
    confirmar = messagebox.askyesno(
        "Confirmar envio",
        f"Empresa: {empresa}\nE-mails: {', '.join(emails)}\nTipo: {tipo_envio}\n\nArquivos:\n{lista_arquivos}\n\nDeseja enviar?"
    )
    if not confirmar:
        return

    # SOMENTE AGORA inicia a barra de progresso
    progresso.start()
    root.update()

    def enviar():
        try:
            if tipo_envio == "ambos":
                assunto = f"Nota Fiscal e Boleto – {empresa}"
                corpo = (
                    "Prezados,\n\n"
                    "Segue em anexo, nota fiscal e boleto bancário para pagamento referente a prestação de serviços de coleta.\n\n"
                    "Colocamo-nos à disposição.\n\nAtenciosamente,"
                )
            elif tipo_envio == "nf":
                assunto = f"Nota Fiscal – {empresa}"
                corpo = (
                    "Prezados,\n\n"
                    "Segue em anexo, nota fiscal referente a prestação de serviços de coleta.\n\n"
                    "Colocamo-nos à disposição.\n\nAtenciosamente,"
                )
            elif tipo_envio == "boleto":
                assunto = f"Boleto – {empresa}"
                corpo = (
                    "Prezados,\n\n"
                    "Segue em anexo, boleto bancário para pagamento referente a prestação de serviços de coleta.\n\n"
                    "Colocamo-nos à disposição.\n\nAtenciosamente,"
                )
            else:
                root.after(0, lambda: messagebox.showerror("Erro", f"Tipo de envio inválido: {tipo_envio}"))
                return

            yag = yagmail.SMTP(SEU_EMAIL, SENHA_APP)
            yag.send(to=emails, subject=assunto, contents=corpo, attachments=anexos)

            # Exibe o sucesso só DEPOIS de parar a barra
            root.after(0, lambda: [
                progresso.stop(),
                messagebox.showinfo("Sucesso", f"E-mail enviado com sucesso para {empresa}.")
            ])

        except Exception as e:
            root.after(0, lambda: [
                progresso.stop(),
                messagebox.showerror("Erro ao enviar", f"Erro ao enviar e-mail para {empresa}:\n{e}")
            ])

    # Roda o envio em uma thread separada
    threading.Thread(target=enviar).start()

root = tk.Tk()
root.title("Envio Automático de E-mails Dilix")
root.geometry("800x600")

abas = ttk.Notebook(root)
aba_principal = ttk.Frame(abas)
aba_config = ttk.Frame(abas)
abas.add(aba_principal, text="Principal")
abas.add(aba_config, text="Configurações")
abas.pack(expand=1, fill="both")

# Aba de Configurações
tk.Label(aba_config, text="Caminho da planilha:").pack(pady=5)
entrada_planilha = tk.Entry(aba_config, width=80)
entrada_planilha.pack()
tk.Button(aba_config, text="Selecionar Planilha", command=escolher_planilha).pack(pady=5)
progresso = ttk.Progressbar(aba_principal, orient="horizontal", mode="indeterminate", length=400)
progresso.pack(pady=10)


tk.Label(aba_config, text="Pasta raiz:").pack(pady=5)
entrada_pasta = tk.Entry(aba_config, width=80)
entrada_pasta.pack()
tk.Button(aba_config, text="Selecionar Pasta", command=escolher_pasta_raiz).pack(pady=5)

tk.Label(aba_config, text="Mês da pasta (ex: Agosto 2025):").pack(pady=5)
entrada_mes = tk.Entry(aba_config, width=40)
entrada_mes.pack()
tk.Button(aba_config, text="Definir Pasta do Mês", command=definir_pasta_mes).pack(pady=10)

tk.Button(aba_config, text="Carregar Clientes da Planilha", command=carregar_clientes).pack(pady=10)

# Aba Principal
tk.Label(aba_principal, text="Selecione uma empresa:").pack(pady=5)
lista_clientes = tk.Listbox(aba_principal, width=90, height=20)
lista_clientes.pack(pady=10)

tk.Button(aba_principal, text="Enviar E-mail para Selecionado", command=enviar_email_cliente).pack(pady=10)
label_creditos = tk.Label(root, text="Desenvolvido por Hudson Mesquita Souza - 2025                  Envio Auto V1.15", font=("Arial", 9), fg="gray")
label_creditos.pack(side=tk.BOTTOM, pady=5)
# === Carrega CONFIG no início ===
carregar_config()
entrada_planilha.insert(0, config.get("planilha", ""))
entrada_pasta.insert(0, config.get("pasta_raiz", ""))

root.mainloop()
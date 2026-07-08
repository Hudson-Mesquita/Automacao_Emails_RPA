import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import pandas as pd
import yagmail
import threading

# === CONFIGURAÇÕES INICIAIS ===
SEU_EMAIL = "d....."
SENHA_APP = "h....."

COL_EMPRESA = "Empresa"
COL_EMAILS = "E-mails"
COL_PASTA = "Pasta"
COL_TIPO_ENVIO = "Tipo de Envio"

CONFIG_PATH = "config.json"
config = {"planilha": "", "pasta_raiz": ""}
df = None
pasta_mes_atual = ""

# === FUNÇÕES DE CONFIG ===

def salvar_config():
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def carregar_config():
    global config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

# === GUI ===

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

# === FUNÇÃO DE EDIÇÃO E ENVIO ===

def editar_e_confirmar_envio(empresa, emails, assunto, corpo_inicial, anexos):
    def enviar_depois_edicao():
        corpo_editado = campo_texto.get("1.0", tk.END)
        try:
            yag = yagmail.SMTP(SEU_EMAIL, SENHA_APP)
            yag.send(to=emails, subject=assunto, contents=corpo_editado, attachments=anexos)
            janela.destroy()
            messagebox.showinfo("Sucesso", f"E-mail enviado com sucesso para {empresa}.")
        except Exception as e:
            messagebox.showerror("Erro ao enviar", f"Erro ao enviar e-mail para {empresa}:\n{e}")
            janela.destroy()

    janela = tk.Toplevel(root)
    janela.title(f"Editar E-mail – {empresa}")
    janela.geometry("600x500")

    tk.Label(janela, text=f"Para: {', '.join(emails)}").pack(pady=5)
    tk.Label(janela, text=f"Assunto: {assunto}").pack(pady=5)

    campo_texto = tk.Text(janela, wrap="word", font=("Arial", 10))
    campo_texto.pack(expand=True, fill="both", padx=10, pady=10)
    campo_texto.insert("1.0", corpo_inicial)

    if anexos:
        frame_anexos = tk.Frame(janela)
        frame_anexos.pack(pady=5)
        tk.Label(frame_anexos, text="Anexos:").pack()
        for a in anexos:
            tk.Label(frame_anexos, text=os.path.basename(a), fg="blue").pack()

    tk.Button(janela, text="Enviar E-mail", command=enviar_depois_edicao).pack(pady=10)

# === ENVIO INDIVIDUAL ===

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
    emails = [e.strip() for e in str(linha[COL_EMAILS]).replace(";", ",").split(",") if e.strip()]
    nome_pasta = linha[COL_PASTA]
    tipo_envio = linha[COL_TIPO_ENVIO].strip().lower()

    caminho_empresa = os.path.join(pasta_mes_atual, nome_pasta)
    if not os.path.isdir(caminho_empresa):
        messagebox.showwarning("Pasta não encontrada", f"Pasta '{nome_pasta}' não existe.")
        return

    arquivos_pdf = [os.path.join(caminho_empresa, f) for f in os.listdir(caminho_empresa) if f.lower().endswith(".pdf")]
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

    if tipo_envio == "ambos":
        assunto = f"Nota Fiscal e Boleto – {empresa}"
        corpo = (
            "Prezados,\n\n"
            "Segue em anexo, nota fiscal e boleto bancário para pagamento referente à prestação de serviços \n\n"
            "Colocamo-nos à disposição.\n\nAtenciosamente,"
        )
    elif tipo_envio == "nf":
        assunto = f"Nota Fiscal – {empresa}"
        corpo = (
            "Prezados,\n\n"
            "Segue em anexo, nota fiscal referente à prestação de serviços .\n\n"
            "Colocamo-nos à disposição.\n\nAtenciosamente,"
        )
    elif tipo_envio == "boleto":
        assunto = f"Boleto – {empresa}"
        corpo = (
            "Prezados,\n\n"
            "Segue em anexo, boleto bancário para pagamento referente à prestação de serviços.\n\n"
            "Colocamo-nos à disposição.\n\nAtenciosamente,"
        )
    else:
        messagebox.showerror("Erro", f"Tipo de envio inválido: {tipo_envio}")
        return

    editar_e_confirmar_envio(empresa, emails, assunto, corpo, anexos)

# === ENVIO EM LOTE (SEM MUDANÇAS) ===

def enviar_em_lote():
    selecionados = lista_clientes.curselection()
    if not selecionados:
        messagebox.showwarning("Aviso", "Selecione ao menos um cliente.")
        return
    if not pasta_mes_atual:
        messagebox.showerror("Erro", "Defina a pasta do mês primeiro.")
        return

    total = len(selecionados)
    progresso["maximum"] = total
    progresso["value"] = 0

    # Desativa botão e inicia spinner
    botao_enviar_lote.config(state="disabled")
    animando = True
    texto_spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner_index = [0]

    spinner_label = tk.Label(aba_principal, text="Enviando... ⠋", font=("Arial", 10, "italic"), fg="blue")
    spinner_label.pack()

    def atualizar_spinner():
        if animando:
            spinner_label.config(text=f"Enviando... {texto_spinner[spinner_index[0] % len(texto_spinner)]}")
            spinner_index[0] += 1
            root.after(100, atualizar_spinner)

    atualizar_spinner()

    def enviar_todos():
        enviados = []
        erros = []

        for i, idx in enumerate(selecionados):
            try:
                linha = df.iloc[idx]
                empresa = linha[COL_EMPRESA]
                emails = [e.strip() for e in str(linha[COL_EMAILS]).replace(";", ",").split(",") if e.strip()]
                nome_pasta = linha[COL_PASTA]
                tipo_envio = linha[COL_TIPO_ENVIO].strip().lower()
                caminho_empresa = os.path.join(pasta_mes_atual, nome_pasta)

                if not os.path.isdir(caminho_empresa):
                    erros.append(f"{empresa}: Pasta '{nome_pasta}' não encontrada.")
                    continue

                arquivos_pdf = [os.path.join(caminho_empresa, f) for f in os.listdir(caminho_empresa) if f.lower().endswith(".pdf")]
                if not arquivos_pdf:
                    erros.append(f"{empresa}: Nenhum PDF encontrado.")
                    continue

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
                    erros.append(f"{empresa}: Nenhum anexo do tipo '{tipo_envio}' encontrado.")
                    continue

                if tipo_envio == "ambos":
                    assunto = f"Nota Fiscal e Boleto – {empresa}"
                    corpo = (
                        "Prezados,\n\nSegue em anexo, nota fiscal e boleto bancário para pagamento referente à prestação de serviços de coleta.\n\nColocamo-nos à disposição.\n\nAtenciosamente,"
                    )
                elif tipo_envio == "nf":
                    assunto = f"Nota Fiscal – {empresa}"
                    corpo = (
                        "Prezados,\n\nSegue em anexo, nota fiscal referente à prestação de serviços de coleta.\n\nColocamo-nos à disposição.\n\nAtenciosamente,"
                    )
                elif tipo_envio == "boleto":
                    assunto = f"Boleto – {empresa}"
                    corpo = (
                        "Prezados,\n\nSegue em anexo, boleto bancário para pagamento referente à prestação de serviços de coleta.\n\nColocamo-nos à disposição.\n\nAtenciosamente,"
                    )
                else:
                    erros.append(f"{empresa}: Tipo de envio inválido '{tipo_envio}'.")
                    continue

                yag = yagmail.SMTP(SEU_EMAIL, SENHA_APP)
                yag.send(to=emails, subject=assunto, contents=corpo, attachments=anexos)
                enviados.append(empresa)

            except Exception as e:
                erros.append(f"{empresa}: Erro ao enviar – {e}")

            progresso["value"] += 1
            root.update()

        # Parar spinner e reativar botão
        def finalizar_interface():
            nonlocal animando
            animando = False
            spinner_label.destroy()
            progresso["value"] = 0  # <-- RESET DA PROGRESSBAR
            botao_enviar_lote.config(state="normal")

            resumo = f"E-mails enviados com sucesso: {len(enviados)}\n"
            resumo += "\n".join([f"✔ {nome}" for nome in enviados])
            if erros:
                resumo += f"\n\nOcorreram {len(erros)} erro(s):\n" + "\n".join([f"✖ {e}" for e in erros])

            messagebox.showinfo("Resumo do Envio", resumo)

        root.after(0, finalizar_interface)

    threading.Thread(target=enviar_todos).start()


# === INTERFACE PRINCIPAL ===

root = tk.Tk()
root.title("Envio Automático de E-mails – V1.20")
root.geometry("800x600")

abas = ttk.Notebook(root)
aba_principal = ttk.Frame(abas)
aba_config = ttk.Frame(abas)
abas.add(aba_principal, text="Principal")
abas.add(aba_config, text="Configurações")
abas.pack(expand=1, fill="both")

# Configurações
tk.Label(aba_config, text="Caminho da planilha:").pack()
entrada_planilha = tk.Entry(aba_config, width=80)
entrada_planilha.pack()
tk.Button(aba_config, text="Selecionar Planilha", command=escolher_planilha).pack(pady=5)

tk.Label(aba_config, text="Pasta raiz:").pack()
entrada_pasta = tk.Entry(aba_config, width=80)
entrada_pasta.pack()
tk.Button(aba_config, text="Selecionar Pasta", command=escolher_pasta_raiz).pack(pady=5)

tk.Label(aba_config, text="Mês da pasta (ex: Agosto 2025):").pack()
entrada_mes = tk.Entry(aba_config, width=40)
entrada_mes.pack()
tk.Button(aba_config, text="Definir Pasta do Mês", command=definir_pasta_mes).pack(pady=10)
tk.Button(aba_config, text="Carregar Clientes da Planilha", command=carregar_clientes).pack(pady=10)

# Principal
tk.Label(aba_principal, text="Selecione uma empresa:").pack()
lista_clientes = tk.Listbox(aba_principal, width=90, height=20, selectmode=tk.EXTENDED)
lista_clientes.pack(pady=10)

tk.Button(aba_principal, text="Enviar E-mail para Selecionado", command=enviar_email_cliente).pack(pady=10)
botao_enviar_lote = tk.Button(aba_principal, text="Enviar E-mail em lote", command=enviar_em_lote)
botao_enviar_lote.pack()

progresso = ttk.Progressbar(aba_principal, orient="horizontal", mode="determinate", length=400)
progresso.pack(pady=10)

label_creditos = tk.Label(root, text="Desenvolvido por Hudson Mesquita Souza - 2025                  Envio Auto V1.20", font=("Arial", 9), fg="gray")
label_creditos.pack(side=tk.BOTTOM, pady=5)

carregar_config()
entrada_planilha.insert(0, config.get("planilha", ""))
entrada_pasta.insert(0, config.get("pasta_raiz", ""))

root.mainloop()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import pandas as pd
import yagmail
import threading

# === CONFIGURAÇÕES INICIAIS ===
SEU_EMAIL = "d......."
SENHA_APP = "h......."

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


def abrir_janela_adicionar_cliente():
    if not config.get("planilha"):
        messagebox.showerror("Erro", "Selecione uma planilha antes.")
        return

    janela_add = tk.Toplevel(root)
    janela_add.title("Adicionar Novo Cliente")
    janela_add.geometry("400x300")

    # Labels e Entradas
    tk.Label(janela_add, text="Empresa:").pack()
    entrada_empresa = tk.Entry(janela_add, width=50)
    entrada_empresa.pack()

    tk.Label(janela_add, text="E-mails (separados por vírgula ou ponto e vírgula):").pack()
    entrada_emails = tk.Entry(janela_add, width=50)
    entrada_emails.pack()

    tk.Label(janela_add, text="Nome da Pasta:").pack()
    entrada_pasta = tk.Entry(janela_add, width=50)
    entrada_pasta.pack()

    tk.Label(janela_add, text="Tipo de Envio (boleto, nf, ambos):").pack()
    entrada_tipo = tk.Entry(janela_add, width=50)
    entrada_tipo.pack()

    def salvar_cliente():
        empresa = entrada_empresa.get().strip()
        emails = entrada_emails.get().strip()
        pasta = entrada_pasta.get().strip()
        tipo = entrada_tipo.get().strip().lower()

        if not all([empresa, emails, pasta, tipo]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
            return

        if tipo not in ["boleto", "nf", "ambos"]:
            messagebox.showerror("Erro", "Tipo de envio deve ser: boleto, nf ou ambos.")
            return

        try:
            nova_linha = pd.DataFrame([{
                COL_EMPRESA: empresa,
                COL_EMAILS: emails,
                COL_PASTA: pasta,
                COL_TIPO_ENVIO: tipo
            }])

            # Carrega, adiciona e salva
            df_existente = pd.read_excel(config["planilha"])
            df_atualizado = pd.concat([df_existente, nova_linha], ignore_index=True)
            df_atualizado.to_excel(config["planilha"], index=False)

            messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso.")
            janela_add.destroy()
            carregar_clientes()  # Atualiza a lista na interface
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar cliente:\n{e}")

    tk.Button(janela_add, text="Salvar Cliente", command=salvar_cliente).pack(pady=15)

def carregar_config():
    global config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

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
        raise e

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

# === CRIAÇÃO DA INTERFACE COM ABAS ===

root = tk.Tk()
root.title("Envio de E-mails Automático V1.22")
root.geometry("900x620")

abas = ttk.Notebook(root)
aba_envio = ttk.Frame(abas)
aba_config = ttk.Frame(abas)
abas.add(aba_envio, text="Envio")
abas.add(aba_config, text="Configurações")
abas.pack(fill="both", expand=True, padx=10, pady=10)

# === ABA CONFIGURAÇÃO ===

frame_planilha = ttk.Frame(aba_config)
frame_planilha.pack(fill="x", pady=10)
ttk.Label(frame_planilha, text="Planilha:").pack(side="left")
entrada_planilha = ttk.Entry(frame_planilha, width=60)
entrada_planilha.pack(side="left", padx=5)
ttk.Button(frame_planilha, text="Selecionar", command=escolher_planilha).pack(side="left")

frame_pasta = ttk.Frame(aba_config)
frame_pasta.pack(fill="x", pady=10)
ttk.Label(frame_pasta, text="Pasta Raiz:").pack(side="left")
entrada_pasta = ttk.Entry(frame_pasta, width=60)
entrada_pasta.pack(side="left", padx=5)
ttk.Button(frame_pasta, text="Selecionar", command=escolher_pasta_raiz).pack(side="left")
tk.Button(aba_config, text="Adicionar Novo Cliente", command=abrir_janela_adicionar_cliente).pack(pady=10)


# === ABA ENVIO ===

botao_carregar = ttk.Button(aba_envio, text="Carregar Clientes", command=carregar_clientes)
botao_carregar.pack(pady=10)

lista_clientes = tk.Listbox(aba_envio, height=15)
lista_clientes.pack(fill="both", expand=True, pady=5)

frame_mes = ttk.Frame(aba_envio)
frame_mes.pack(fill="x", pady=5)
ttk.Label(frame_mes, text="Nome da pasta do mês:").pack(side="left")
entrada_mes = ttk.Entry(frame_mes, width=30)
entrada_mes.pack(side="left", padx=5)
ttk.Button(frame_mes, text="Definir Pasta Mês", command=definir_pasta_mes).pack(side="left")

frame_envio = ttk.Frame(aba_envio)
frame_envio.pack(fill="x", pady=10)
botao_enviar = ttk.Button(frame_envio, text="Enviar E-mail Cliente", command=None)  # será definido depois
botao_enviar.pack(side="left", padx=5)
botao_enviar_lote = ttk.Button(frame_envio, text="Enviar em Lote", command=None)  # será definido depois
botao_enviar_lote.pack(side="left", padx=5)

progresso = ttk.Progressbar(aba_envio, orient="horizontal", length=400, mode="determinate")
progresso.pack(pady=10)

# Créditos
creditos = tk.Label(root, text="Desenvolvido por Hudson Mesquita Souza – 2025", fg="gray", font=("Arial", 9, "italic"))
creditos.pack(pady=(0, 5))

# === INICIALIZA CONFIG E TENTA CARREGAR PLANILHA ===

carregar_config()
entrada_planilha.insert(0, config.get("planilha", ""))
entrada_pasta.insert(0, config.get("pasta_raiz", ""))

try:
    carregar_clientes()
except Exception as e:
    messagebox.showerror(
        "Falha ao carregar a planilha",
        f"Falha ao carregar a planilha automaticamente:\n{e}\n"
        "Atualize o caminho e verifique se está no formato correto."
    )
# === FUNÇÃO DE EDIÇÃO E ENVIO ===

def editar_e_confirmar_envio(empresa, emails, assunto, corpo_inicial, anexos):
    def enviar_depois_edicao():
        corpo_editado = campo_texto.get("1.0", tk.END)
        btn_enviar.config(state="disabled")
        animando[0] = True
        atualizar_spinner()

        def enviar_email():
            try:
                yag = yagmail.SMTP(SEU_EMAIL, SENHA_APP)
                yag.send(to=emails, subject=assunto, contents=corpo_editado, attachments=anexos)
                animando[0] = False
                janela.after(100, lambda: janela.destroy())
                messagebox.showinfo("Sucesso", f"E-mail enviado com sucesso para {empresa}.")
            except Exception as e:
                animando[0] = False
                messagebox.showerror("Erro", f"Erro ao enviar para {empresa}:\n{e}")
                btn_enviar.config(state="normal")

        threading.Thread(target=enviar_email, daemon=True).start()

    janela = tk.Toplevel(root)
    janela.title(f"Editar E-mail – {empresa}")
    janela.geometry("700x500")
    janela.minsize(600, 400)

    janela.grid_rowconfigure(2, weight=1)
    janela.grid_columnconfigure(1, weight=1)

    tk.Label(janela, text=f"Para: {', '.join(emails)}").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    tk.Label(janela, text=f"Assunto: {assunto}").grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)

    campo_texto = tk.Text(janela, wrap="word", font=("Arial", 10))
    campo_texto.grid(row=2, column=0, sticky="nsew", padx=(10, 0), pady=5)

    scrollbar = ttk.Scrollbar(janela, orient="vertical", command=campo_texto.yview)
    scrollbar.grid(row=2, column=1, sticky="ns", padx=(0, 10), pady=5)
    campo_texto.config(yscrollcommand=scrollbar.set)
    campo_texto.insert("1.0", corpo_inicial)

    if anexos:
        frame_anexos = tk.Frame(janela)
        frame_anexos.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Label(frame_anexos, text="Anexos:").pack(anchor="w")
        for a in anexos:
            tk.Label(frame_anexos, text=os.path.basename(a), fg="blue").pack(anchor="w")

    spinner_label = tk.Label(janela, text="", font=("Arial", 10, "italic"), fg="blue")
    spinner_label.grid(row=4, column=0, sticky="w", padx=10)

    texto_spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner_index = [0]
    animando = [False]

    def atualizar_spinner():
        if animando[0]:
            spinner_label.config(text=f"Enviando... {texto_spinner[spinner_index[0] % len(texto_spinner)]}")
            spinner_index[0] += 1
            janela.after(100, atualizar_spinner)
        else:
            spinner_label.config(text="")

    btn_enviar = tk.Button(janela, text="Enviar E-mail", command=enviar_depois_edicao)
    btn_enviar.grid(row=5, column=0, columnspan=2, sticky="e", padx=10, pady=10)

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
        messagebox.showwarning("Sem anexos", f"Nenhum PDF do tipo '{tipo_envio}' encontrado.")
        return

    assunto = f"{'Nota Fiscal e Boleto' if tipo_envio == 'ambos' else 'Nota Fiscal' if tipo_envio == 'nf' else 'Boleto'} – {empresa}"
    corpo = (
        "Prezados,\n\n"
        f"Segue em anexo, {assunto.lower()} referente à prestação de serviços.\n\n"
        "Colocamo-nos à disposição.\n\nAtenciosamente,"
    )

    editar_e_confirmar_envio(empresa, emails, assunto, corpo, anexos)

# === ENVIO EM LOTE ===

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

    botao_enviar_lote.config(state="disabled")
    animando = True
    texto_spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner_index = [0]

    spinner_label = tk.Label(aba_envio, text="Enviando... ⠋", font=("Arial", 10, "italic"), fg="blue")
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

        for idx in selecionados:
            try:
                linha = df.iloc[idx]
                empresa = linha[COL_EMPRESA]
                emails = [e.strip() for e in str(linha[COL_EMAILS]).replace(";", ",").split(",") if e.strip()]
                nome_pasta = linha[COL_PASTA]
                tipo_envio = linha[COL_TIPO_ENVIO].strip().lower()
                caminho_empresa = os.path.join(pasta_mes_atual, nome_pasta)

                if not os.path.isdir(caminho_empresa):
                    erros.append(f"{empresa}: Pasta não encontrada.")
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
                    erros.append(f"{empresa}: Nenhum PDF do tipo '{tipo_envio}' encontrado.")
                    continue

                assunto = f"{'Nota Fiscal e Boleto' if tipo_envio == 'ambos' else 'Nota Fiscal' if tipo_envio == 'nf' else 'Boleto'} – {empresa}"
                corpo = (
                    "Prezados,\n\n"
                    f"Segue em anexo, {assunto.lower()} referente à prestação de serviços.\n\n"
                    "Colocamo-nos à disposição.\n\nAtenciosamente,"
                )

                yag = yagmail.SMTP(SEU_EMAIL, SENHA_APP)
                yag.send(to=emails, subject=assunto, contents=corpo, attachments=anexos)
                enviados.append(empresa)
                progresso["value"] += 1
                root.update_idletasks()

            except Exception as e:
                erros.append(f"{empresa}: {str(e)}")

        # Encerrar
        nonlocal animando
        animando = False
        spinner_label.destroy()
        botao_enviar_lote.config(state="normal")

        msg = f"E-mails enviados: {len(enviados)}\n"
        if erros:
            msg += "\nOcorreram erros:\n" + "\n".join(erros)
        messagebox.showinfo("Resultado do envio", msg)

    threading.Thread(target=enviar_todos, daemon=True).start()


# === VÍNCULO FINAL DOS BOTÕES ===

botao_enviar.config(command=enviar_email_cliente)
botao_enviar_lote.config(command=enviar_em_lote)

# === INICIAR INTERFACE ===
root.mainloop()

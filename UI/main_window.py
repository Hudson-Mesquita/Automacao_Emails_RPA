import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from Services.config_service import salvar_config
from UI.add_cliente_window import AddClienteWindow
from UI.edit_email_window import EditEmailWindow


class MainWindow:
    def __init__(self, config, cliente_service):
        self.config = config
        self.cliente_service = cliente_service
        self.pasta_mes_atual = ""
        
        # Componentes da UI
        self.root = None
        self.entrada_planilha = None
        self.entrada_pasta = None
        self.lista_clientes = None
        self.entrada_mes = None
        self.progresso = None
        self.botao_enviar_lote = None
        
        # Janelas filhas
        self.add_cliente_window = None
        self.edit_email_window = None
    
    def create_window(self):
        """Cria e configura a janela principal"""
        self.root = tk.Tk()
        self.root.title("Envio de E-mails Automático V1.21")
        self.root.geometry("900x620")
        
        self._create_tabs()
        self._create_config_tab()
        self._create_envio_tab()
        self._create_credits()
        
        return self.root
    
    def _create_tabs(self):
        """Cria as abas principais"""
        self.abas = ttk.Notebook(self.root)
        self.aba_envio = ttk.Frame(self.abas)
        self.aba_config = ttk.Frame(self.abas)
        self.abas.add(self.aba_envio, text="Envio")
        self.abas.add(self.aba_config, text="Configurações")
        self.abas.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_config_tab(self):
        """Cria a aba de configurações"""
        # Frame da planilha
        frame_planilha = ttk.Frame(self.aba_config)
        frame_planilha.pack(fill="x", pady=10)
        ttk.Label(frame_planilha, text="Planilha:").pack(side="left")
        self.entrada_planilha = ttk.Entry(frame_planilha, width=60)
        self.entrada_planilha.pack(side="left", padx=5)
        ttk.Button(frame_planilha, text="Selecionar", command=self._escolher_planilha).pack(side="left")

        # Frame da pasta
        frame_pasta = ttk.Frame(self.aba_config)
        frame_pasta.pack(fill="x", pady=10)
        ttk.Label(frame_pasta, text="Pasta Raiz:").pack(side="left")
        self.entrada_pasta = ttk.Entry(frame_pasta, width=60)
        self.entrada_pasta.pack(side="left", padx=5)
        ttk.Button(frame_pasta, text="Selecionar", command=self._escolher_pasta_raiz).pack(side="left")
        
        # Botão adicionar cliente
        ttk.Button(self.aba_config, text="Adicionar Novo Cliente", command=self._abrir_janela_adicionar_cliente).pack(pady=10)
    
    def _create_envio_tab(self):
        """Cria a aba de envio"""
        # Botão carregar clientes
        ttk.Button(self.aba_envio, text="Carregar Clientes", command=self._carregar_clientes).pack(pady=10)

        # Lista de clientes
        self.lista_clientes = tk.Listbox(self.aba_envio, height=15)
        self.lista_clientes.pack(fill="both", expand=True, pady=5)

        # Frame do mês
        frame_mes = ttk.Frame(self.aba_envio)
        frame_mes.pack(fill="x", pady=5)
        ttk.Label(frame_mes, text="Nome da pasta do mês:").pack(side="left")
        self.entrada_mes = ttk.Entry(frame_mes, width=30)
        self.entrada_mes.pack(side="left", padx=5)
        ttk.Button(frame_mes, text="Definir Pasta Mês", command=self._definir_pasta_mes).pack(side="left")

        # Frame de envio
        frame_envio = ttk.Frame(self.aba_envio)
        frame_envio.pack(fill="x", pady=10)
        ttk.Button(frame_envio, text="Enviar E-mail Cliente", command=self._enviar_email_cliente).pack(side="left", padx=5)
        self.botao_enviar_lote = ttk.Button(frame_envio, text="Enviar em Lote", command=self._enviar_em_lote)
        self.botao_enviar_lote.pack(side="left", padx=5)

        # Barra de progresso
        self.progresso = ttk.Progressbar(self.aba_envio, orient="horizontal", length=400, mode="determinate")
        self.progresso.pack(pady=10)
    
    def _create_credits(self):
        """Cria os créditos"""
        creditos = tk.Label(self.root, text="Desenvolvido por Hudson Mesquita Souza – 2025", 
                          fg="gray", font=("Arial", 9, "italic"))
        creditos.pack(pady=(0, 5))
    
    def initialize_fields(self):
        """Inicializa os campos com os valores do config"""
        self.entrada_planilha.insert(0, self.config.get("planilha", ""))
        self.entrada_pasta.insert(0, self.config.get("pasta_raiz", ""))
    
    # === MÉTODOS DE CONFIGURAÇÃO ===
    
    def _escolher_planilha(self):
        """Abre diálogo para escolher planilha"""
        caminho = filedialog.askopenfilename(filetypes=[("Planilhas Excel", "*.xlsx *.xls")])
        if caminho:
            self.config["planilha"] = caminho
            self.entrada_planilha.delete(0, tk.END)
            self.entrada_planilha.insert(0, caminho)
            salvar_config(self.config)
    
    def _escolher_pasta_raiz(self):
        """Abre diálogo para escolher pasta raiz"""
        pasta = filedialog.askdirectory()
        if pasta:
            self.config["pasta_raiz"] = pasta
            self.entrada_pasta.delete(0, tk.END)
            self.entrada_pasta.insert(0, pasta)
            salvar_config(self.config)
    
    def _abrir_janela_adicionar_cliente(self):
        """Abre a janela para adicionar novo cliente"""
        self.add_cliente_window = AddClienteWindow(
            self.root, 
            self.cliente_service, 
            self._carregar_clientes
        )
        self.add_cliente_window.show()
    
    # === MÉTODOS DE ENVIO ===
    
    def _carregar_clientes(self):
        """Carrega os clientes na lista"""
        try:
            self.cliente_service.carregar_clientes()
            
            # Atualiza a UI
            self.lista_clientes.delete(0, tk.END)
            for item in self.cliente_service.get_lista_clientes_formatada():
                self.lista_clientes.insert(tk.END, item)
                
            messagebox.showinfo("Sucesso", "Clientes carregados.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar clientes:\n{e}")
    
    def _definir_pasta_mes(self):
        """Define a pasta do mês atual"""
        mes = self.entrada_mes.get().strip()
        if not mes:
            messagebox.showerror("Erro", "Digite o nome da pasta do mês (ex: Agosto 2025)")
            return
        pasta = os.path.join(self.config["pasta_raiz"], mes)
        if not os.path.exists(pasta):
            messagebox.showerror("Erro", f"Pasta '{pasta}' não encontrada.")
            return
        self.pasta_mes_atual = pasta
        messagebox.showinfo("Pasta definida", f"Pasta do mês definida como:\n{pasta}")
    
    def _enviar_email_cliente(self):
        """Envia e-mail para o cliente selecionado"""
        selecionado = self.lista_clientes.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente da lista.")
            return
        if not self.pasta_mes_atual:
            messagebox.showerror("Erro", "Defina a pasta do mês primeiro.")
            return

        try:
            idx = selecionado[0]
            dados = self.cliente_service.preparar_dados_envio(idx, self.pasta_mes_atual)
            
            self.edit_email_window = EditEmailWindow(self.root)
            self.edit_email_window.show(
                dados['empresa'], 
                dados['emails'], 
                dados['assunto'], 
                dados['corpo'], 
                dados['anexos']
            )
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao preparar envio:\n{e}")
    
    def _enviar_em_lote(self):
        """Envia e-mails em lote"""
        selecionados = self.lista_clientes.curselection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione ao menos um cliente.")
            return
        if not self.pasta_mes_atual:
            messagebox.showerror("Erro", "Defina a pasta do mês primeiro.")
            return

        total = len(selecionados)
        self.progresso["maximum"] = total
        self.progresso["value"] = 0

        self.botao_enviar_lote.config(state="disabled")
        animando = True
        texto_spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spinner_index = [0]

        spinner_label = tk.Label(self.aba_envio, text="Enviando... ⠋", font=("Arial", 10, "italic"), fg="blue")
        spinner_label.pack()

        def atualizar_spinner():
            if animando:
                spinner_label.config(text=f"Enviando... {texto_spinner[spinner_index[0] % len(texto_spinner)]}")
                spinner_index[0] += 1
                self.root.after(100, atualizar_spinner)

        atualizar_spinner()

        def enviar_todos():
            enviados = []
            erros = []

            for dados in self.cliente_service.preparar_dados_envio_lote(selecionados, self.pasta_mes_atual):
                if 'erro' in dados:
                    erros.append(dados['erro'])
                    continue

                try:
                    from Services.email_service import enviar_email as enviar_email_service
                    enviar_email_service(
                        dados['emails'], 
                        dados['assunto'], 
                        dados['corpo'], 
                        dados['anexos']
                    )
                    enviados.append(dados['empresa'])
                    self.progresso["value"] += 1
                    self.root.update_idletasks()

                except Exception as e:
                    erros.append(f"{dados['empresa']}: {str(e)}")

            # Encerrar
            nonlocal animando
            animando = False
            spinner_label.destroy()
            self.botao_enviar_lote.config(state="normal")

            msg = f"E-mails enviados: {len(enviados)}\n"
            if erros:
                msg += "\nOcorreram erros:\n" + "\n".join(erros)
            messagebox.showinfo("Resultado do envio", msg)

        threading.Thread(target=enviar_todos, daemon=True).start()
    
    def run(self):
        """Inicia o loop principal da aplicação"""
        self.root.mainloop()

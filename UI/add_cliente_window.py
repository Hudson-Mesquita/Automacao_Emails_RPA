import tkinter as tk
from tkinter import messagebox


class AddClienteWindow:
    def __init__(self, parent, cliente_service, on_success_callback):
        self.parent = parent
        self.cliente_service = cliente_service
        self.on_success_callback = on_success_callback
        self.window = None
    
    def show(self):
        """Mostra a janela de adicionar cliente"""
        if not self.cliente_service.config.get("planilha"):
            messagebox.showerror("Erro", "Selecione uma planilha antes.")
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Adicionar Novo Cliente")
        self.window.geometry("400x300")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Cria os widgets da janela"""
        # Labels e Entradas
        tk.Label(self.window, text="Empresa:").pack()
        self.entrada_empresa = tk.Entry(self.window, width=50)
        self.entrada_empresa.pack()

        tk.Label(self.window, text="E-mails (separados por vírgula ou ponto e vírgula):").pack()
        self.entrada_emails = tk.Entry(self.window, width=50)
        self.entrada_emails.pack()

        tk.Label(self.window, text="Nome da Pasta:").pack()
        self.entrada_pasta = tk.Entry(self.window, width=50)
        self.entrada_pasta.pack()

        tk.Label(self.window, text="Tipo de Envio (boleto, nf, ambos):").pack()
        self.entrada_tipo = tk.Entry(self.window, width=50)
        self.entrada_tipo.pack()

        tk.Button(self.window, text="Salvar Cliente", command=self._salvar_cliente).pack(pady=15)
    
    def _salvar_cliente(self):
        """Salva o cliente usando o serviço"""
        empresa = self.entrada_empresa.get().strip()
        emails = self.entrada_emails.get().strip()
        pasta = self.entrada_pasta.get().strip()
        tipo = self.entrada_tipo.get().strip().lower()

        try:
            self.cliente_service.adicionar_cliente(empresa, emails, pasta, tipo)
            messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso.")
            self.window.destroy()
            
            # Chama o callback para atualizar a lista na interface principal
            if self.on_success_callback:
                self.on_success_callback()
                
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar cliente:\n{e}")

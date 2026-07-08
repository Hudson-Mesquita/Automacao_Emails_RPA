import tkinter as tk
from tkinter import messagebox
import threading
import os
from Services.email_service import enviar_email


class EditEmailWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.campo_texto = None
        self.btn_enviar = None
        self.spinner_label = None
        self.animando = False
        self.spinner_index = 0
        
    def show(self, empresa, emails, assunto, corpo_inicial, anexos):
        """Mostra a janela de edição de e-mail"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Editar E-mail – {empresa}")
        self.window.geometry("700x500")
        self.window.minsize(600, 400)
        
        self.empresa = empresa
        self.emails = emails
        self.assunto = assunto
        self.anexos = anexos
        
        self._create_widgets(corpo_inicial)
        
    def _create_widgets(self, corpo_inicial):
        """Cria os widgets da janela"""
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        # Informações do e-mail
        tk.Label(self.window, text=f"Para: {', '.join(self.emails)}").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5
        )
        tk.Label(self.window, text=f"Assunto: {self.assunto}").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5
        )

        # Campo de texto
        self.campo_texto = tk.Text(self.window, wrap="word", font=("Arial", 10))
        self.campo_texto.grid(row=2, column=0, sticky="nsew", padx=(10, 0), pady=5)
        self.campo_texto.insert("1.0", corpo_inicial)

        # Scrollbar
        scrollbar = tk.ttk.Scrollbar(self.window, orient="vertical", command=self.campo_texto.yview)
        scrollbar.grid(row=2, column=1, sticky="ns", padx=(0, 10), pady=5)
        self.campo_texto.config(yscrollcommand=scrollbar.set)

        # Anexos
        if self.anexos:
            frame_anexos = tk.Frame(self.window)
            frame_anexos.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)
            tk.Label(frame_anexos, text="Anexos:").pack(anchor="w")
            for anexo in self.anexos:
                tk.Label(frame_anexos, text=os.path.basename(anexo), fg="blue").pack(anchor="w")

        # Spinner
        self.spinner_label = tk.Label(self.window, text="", font=("Arial", 10, "italic"), fg="blue")
        self.spinner_label.grid(row=4, column=0, sticky="w", padx=10)

        # Botão de envio
        self.btn_enviar = tk.Button(self.window, text="Enviar E-mail", command=self._enviar_depois_edicao)
        self.btn_enviar.grid(row=5, column=0, columnspan=2, sticky="e", padx=10, pady=10)
    
    def _enviar_depois_edicao(self):
        """Envia o e-mail depois da edição"""
        corpo_editado = self.campo_texto.get("1.0", tk.END)
        self.btn_enviar.config(state="disabled")
        self.animando = True
        self._atualizar_spinner()

        def enviar_email_thread():
            try:
                enviar_email(self.emails, self.assunto, corpo_editado, self.anexos)
                self.animando = False
                self.window.after(100, lambda: self.window.destroy())
                messagebox.showinfo("Sucesso", f"E-mail enviado com sucesso para {self.empresa}.")
            except Exception as e:
                self.animando = False
                messagebox.showerror("Erro", f"Erro ao enviar para {self.empresa}:\n{e}")
                self.btn_enviar.config(state="normal")

        threading.Thread(target=enviar_email_thread, daemon=True).start()
    
    def _atualizar_spinner(self):
        """Atualiza o spinner de envio"""
        texto_spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        if self.animando:
            self.spinner_label.config(text=f"Enviando... {texto_spinner[self.spinner_index % len(texto_spinner)]}")
            self.spinner_index += 1
            self.window.after(100, self._atualizar_spinner)
        else:
            self.spinner_label.config(text="")

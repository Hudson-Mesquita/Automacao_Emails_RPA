"""
Ponto de entrada principal da aplicação de Envio de E-mails Automático.

Este arquivo é responsável apenas por inicializar a aplicação, orquestrando
as diferentes camadas (UI, Serviços, Configuração).
"""

from tkinter import messagebox
from Services.config_service import carregar_config
from Services.cliente_service import ClienteService
from UI.main_window import MainWindow


def main():
    """Função principal que inicializa a aplicação"""
    try:
        # 1. Carrega configurações
        config = carregar_config()
        
        # 2. Inicializa serviços
        cliente_service = ClienteService(config)
        
        # 3. Cria e configura a janela principal
        main_window = MainWindow(config, cliente_service)
        root = main_window.create_window()
        
        # 4. Inicializa campos da UI
        main_window.initialize_fields()
        
        # 5. Tenta carregar clientes automaticamente
        try:
            main_window._carregar_clientes()
        except Exception as e:
            messagebox.showerror(
                "Falha ao carregar a planilha",
                f"Falha ao carregar a planilha automaticamente:\n{e}\n"
                "Atualize o caminho e verifique se está no formato correto."
            )
        
        # 6. Inicia a aplicação
        main_window.run()
        
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Falha ao iniciar a aplicação:\n{e}")


if __name__ == "__main__":
    main()

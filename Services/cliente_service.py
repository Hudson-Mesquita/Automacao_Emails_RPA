import pandas as pd
import os
from constants import *
from Services.file_service import buscar_anexos


class ClienteService:
    def __init__(self, config):
        self.config = config
        self.df = None
    
    def carregar_clientes(self):
        """Carrega os clientes da planilha para o DataFrame"""
        if not self.config.get("planilha"):
            raise ValueError("Selecione uma planilha válida.")
        
        try:
            self.df = pd.read_excel(self.config["planilha"])
            return self.df
        except Exception as e:
            raise Exception(f"Erro ao carregar planilha: {e}")
    
    def adicionar_cliente(self, empresa, emails, pasta, tipo_envio):
        """Adiciona um novo cliente à planilha"""
        if not all([empresa, emails, pasta, tipo_envio]):
            raise ValueError("Todos os campos são obrigatórios.")
        
        if tipo_envio not in ["boleto", "nf", "ambos"]:
            raise ValueError("Tipo de envio deve ser: boleto, nf ou ambos.")
        
        try:
            # Carrega planilha existente
            df_existente = pd.read_excel(self.config["planilha"])
            
            # Cria nova linha
            nova_linha = pd.DataFrame([{
                COL_EMPRESA: empresa,
                COL_EMAILS: emails,
                COL_PASTA: pasta,
                COL_TIPO_ENVIO: tipo_envio
            }])
            
            # Concatena e salva
            df_atualizado = pd.concat([df_existente, nova_linha], ignore_index=True)
            df_atualizado.to_excel(self.config["planilha"], index=False)
            
            # Recarrega o DataFrame
            self.carregar_clientes()
            
        except Exception as e:
            raise Exception(f"Falha ao salvar cliente: {e}")
    
    def get_lista_clientes_formatada(self):
        """Retorna lista de clientes formatada para exibir no Listbox"""
        if self.df is None:
            return []
        
        lista = []
        for idx, row in self.df.iterrows():
            empresa = row.get(COL_EMPRESA, "Sem nome")
            lista.append(f"{idx+1}. {empresa}")
        
        return lista
    
    def preparar_dados_envio(self, idx_selecionado, pasta_mes_atual):
        """Prepara todos os dados necessários para o envio de e-mail"""
        if self.df is None:
            raise ValueError("Carregue os clientes primeiro.")
        
        if idx_selecionado >= len(self.df):
            raise ValueError("Índice de cliente inválido.")
        
        linha = self.df.iloc[idx_selecionado]
        
        # Extrai dados do cliente
        empresa = linha[COL_EMPRESA]
        emails = [e.strip() for e in str(linha[COL_EMAILS]).replace(";", ",").split(",") if e.strip()]
        nome_pasta = linha[COL_PASTA]
        tipo_envio = linha[COL_TIPO_ENVIO].strip().lower()
        
        # Valida pasta
        caminho_empresa = os.path.join(pasta_mes_atual, nome_pasta)
        if not os.path.isdir(caminho_empresa):
            raise ValueError(f"Pasta '{nome_pasta}' não existe.")
        
        # Busca anexos
        anexos = buscar_anexos(caminho_empresa, tipo_envio)
        if not anexos:
            raise ValueError(f"Nenhum PDF do tipo '{tipo_envio}' encontrado.")
        
        # Prepara assunto e corpo
        assunto = self._criar_assunto(empresa, tipo_envio)
        corpo = self._criar_corpo(assunto)
        
        return {
            'empresa': empresa,
            'emails': emails,
            'assunto': assunto,
            'corpo': corpo,
            'anexos': anexos,
            'caminho_empresa': caminho_empresa
        }
    
    def preparar_dados_envio_lote(self, indices_selecionados, pasta_mes_atual):
        """Prepara dados para envio em lote, retornando gerador"""
        for idx in indices_selecionados:
            try:
                yield self.preparar_dados_envio(idx, pasta_mes_atual)
            except Exception as e:
                yield {'erro': f"Cliente {idx}: {str(e)}"}
    
    def _criar_assunto(self, empresa, tipo_envio):
        """Cria o assunto do e-mail baseado no tipo de envio"""
        if tipo_envio == "ambos":
            return f"Nota Fiscal e Boleto – {empresa}"
        elif tipo_envio == "nf":
            return f"Nota Fiscal – {empresa}"
        else:
            return f"Boleto – {empresa}"
    
    def _criar_corpo(self, assunto):
        """Cria o corpo padrão do e-mail"""
        return (
            "Prezados,\n\n"
            f"Segue em anexo, {assunto.lower()} referente à prestação de serviços.\n\n"
            "Colocamo-nos à disposição.\n\nAtenciosamente,"
        )

import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# === CONFIGURAÇÕES INICIAIS ===
SEU_EMAIL = os.getenv("EMAIL_REMETENTE")
SENHA_APP = os.getenv("SENHA_APP_GMAIL")

COL_EMPRESA = "Empresa"
COL_EMAILS = "E-mails"
COL_PASTA = "Pasta"
COL_TIPO_ENVIO = "Tipo de Envio"

CONFIG_PATH = "config.json"
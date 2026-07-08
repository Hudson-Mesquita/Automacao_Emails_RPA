# 📧 Automação de E-mails e Notas Fiscais

> 📊 **Acesse a Apresentação Completa do Projeto (Use Case, Requisitos e Pipeline):** [Presentation.pdf](./Presentation.pdf)

Aplicação desktop desenvolvida em Python (Tkinter) para automatizar o disparo de notas fiscais e boletos em lote. O sistema cruza dados de uma planilha com os arquivos PDF locais e realiza o envio via SMTP do Gmail de forma assíncrona.

## 🚀 Funcionalidades
* Interface gráfica amigável para usuários não-técnicos.
* Leitura de clientes e mapeamento de diretórios via Excel/Pandas.
* Filtro automático de anexos (Boleto, NF ou Ambos).
* Disparo em lote utilizando `threading` para não travar a interface.

## 🛠️ Tecnologias Utilizadas
* **Python 3**
* **Tkinter** (Interface Gráfica)
* **Pandas** (Manipulação de dados da planilha)
* **Yagmail** (Envio de e-mails via SMTP)
* **Dotenv** (Segurança de credenciais)

## ⚙️ Como executar

1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`
3. Crie um arquivo `.env` baseado no `.env.example` e insira suas credenciais do Gmail (Senha de App).
4. Execute o sistema: `python main.py`

## Evolução e Versões Antigas
Este software foi concebido e evoluiu em um cenário real de escritório para resolver o gargalo de faturamentos manuais repetitivos. Caso queira navegar pelo histórico de commits para estudar a evolução, você encontrará o progresso cronológico do código:

    v1.0 (Prova de Conceito): Um script bruto executado puramente via terminal (Email Automático.py), focado em validar a biblioteca de disparo e mapeamento inicial.

    v1.15 a v1.20 (Monólitos Iniciais): Transição para interface gráfica. Foi onde descobri a necessidade de implementar threading após a UI travar em testes de estresse. O código era concentrado em um único arquivo de mais de 400 linhas, focado em UX (bloqueio de botões para evitar cliques duplicados e tratamento do Listbox).

    v1.22 (Transição para Produto): Adição da janela de cadastro de novos clientes direto pela UI, transformando o Excel em um banco de dados invisível para o usuário final.

    v1.30 (Arquitetura Atual): Refatoração completa do monólito para o padrão de responsabilidade única, dividindo o ecossistema em módulos independentes (UI, Services e Constants), além da implementação da segurança de dados com variáveis de ambiente.

⚠️ Nota para testes de versões antigas: Como as versões anteriores à v1.30 são legadas (deprecated), as variáveis de credenciais estavam chumbadas no código (hardcoded). Elas foram limpas e substituídas por tags de marcação (classified). Se você desejar rodar os commits antigos para fins de estudo, precisará editar diretamente as variáveis globais SEU_EMAIL e SENHA_APP com seus dados dentro dos arquivos correspondentes.







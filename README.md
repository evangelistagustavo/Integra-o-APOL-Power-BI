# Integração APOL → Power BI

Integração desenvolvida em Python para consumo do Webservice do APOL, tratamento e persistência dos dados em SQLite e posterior consumo pelo Power BI.

O projeto foi estruturado para realizar atualizações incrementais e automáticas dos dados, utilizando o Agendador de Tarefas do Windows.

---

## Arquitetura

```text
┌─────────────────────┐
│        APOL         │
│     Webservice      │
└──────────┬──────────┘
           │
           │ HTTP / JSON
           ▼
┌─────────────────────┐
│       Python        │
│                     │
│  apol_client.py     │
│  apol_transform.py  │
│  apol_sync.py       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       SQLite        │
│      apol.db        │
│                     │
│     processos       │
│ processos_envolvidos│
└──────────┬──────────┘
           │
           │ Python / ODBC
           ▼
┌─────────────────────┐
│      Power BI       │
│ APOL_integracao.pbix│
└─────────────────────┘

Fluxo de atualização

O processo de atualização segue as seguintes etapas:

1. O Python se conecta ao Webservice do APOL.
2. Os processos são consultados.
3. Os dados recebidos são transformados em DataFrames.
4. Os processos são inseridos ou atualizados no SQLite.
5. Os envolvidos são associados aos respectivos processos.
6. Os IDs recebidos são enviados ao APOL para confirmação da sincronização.
7. A execução é registrada em arquivo de log.
8. O Power BI utiliza o banco SQLite como fonte de dados.

projeto2/
│
├── apol_client.py
├── apol_database.py
├── apol_export.py
├── apol_sync.py
├── apol_transform.py
├── apol_views.py
├── atualizar_apol.py
├── configurar_banco.py
├── validar_banco.py
├── powerbi_apol.py
│
├── apol.db
│
├── logs/
│   └── apol.log
│
├── tests/
│   ├── teste_apol.py
│   ├── teste_apol_dataframe.py
│   ├── teste_upsert.py
│   ├── validar_dados.py
│   └── sincronizar_apol.py
│
├── apol_BI/
│   └── APOL_integracao.pbix
│
├── .env
└── README.md

Principais arquivos
apol_client.py

Responsável pela comunicação com o Webservice do APOL.

Funções principais:

autenticação;
requisição dos processos;
tratamento de erros HTTP;
validação da resposta;
envio da confirmação de sincronização.
apol_transform.py

Responsável pela transformação dos dados recebidos pelo APOL.

São geradas duas estruturas principais:

processos;
processos envolvidos.

Os dados são preparados para armazenamento no SQLite.

apol_sync.py

Responsável pela preparação dos IDs necessários para informar ao APOL quais processos foram sincronizados.

São tratados:

marcas;
marcas internacionais;
patentes;
patentes internacionais.
apol_database.py

Responsável pelas operações relacionadas ao banco SQLite.

Banco utilizado:

apol.db
apol_views.py

Responsável pela criação das views utilizadas para facilitar o consumo dos dados.

Views principais:

vw_processos
vw_processos_envolvidos
atualizar_apol.py

É o principal script da automação.

Executa o fluxo:

Consultar APOL
      ↓
Transformar dados
      ↓
Salvar/atualizar SQLite
      ↓
Preparar IDs
      ↓
Informar sincronização ao APOL
      ↓
Registrar execução

O processo utiliza UPSERT para atualizar registros existentes e inserir novos registros.

powerbi_apol.py

Script auxiliar relacionado ao consumo dos dados pelo Power BI.

validar_banco.py

Utilizado para verificar a integridade do banco.

Exemplos de validações:

quantidade de processos;
quantidade de envolvidos;
existência das tabelas;
consulta de registros.
configurar_banco.py

Utilizado para criação/configuração da estrutura do banco SQLite.

Banco de dados

O projeto utiliza SQLite.

Arquivo:

apol.db
Tabela processos

Armazena informações dos processos, incluindo:

ID;
número do processo;
marca;
classe;
situação;
titular;
natureza;
status;
especificação;
país de origem.
Tabela processos_envolvidos

Relaciona os processos aos envolvidos.

Campos:

ProcessoId
EnvolvidoId
TipoEnvolvido

Atualização incremental

A atualização utiliza UPSERT baseado no campo:

Id

Quando um processo ainda não existe no banco:

INSERT

Quando o processo já existe:

UPDATE

Dessa forma, a execução não precisa reconstruir todo o banco a cada consulta.

Configuração das credenciais

As credenciais do APOL são armazenadas em um arquivo .env.

Exemplo:

APOL_USUARIO=seu_usuario
APOL_SENHA=sua_senha

O arquivo .env não deve ser versionado no GitHub.

Recomenda-se adicionar ao .gitignore:

.env
*.db
logs/
__pycache__/

Dependências

O projeto utiliza Python e as principais bibliotecas:

requests
python-dotenv
pandas

Instalação:

pip install requests python-dotenv pandas

Execução manual

Para executar uma atualização:

py atualizar_apol.py

Uma execução sem alterações apresenta:

Processos recebidos:
0

Nenhum processo novo ou alterado.
Banco permanece inalterado.

Quando existem dados para processamento, os processos são gravados/atualizados no banco e a sincronização é informada ao APOL.

Automação

A atualização é automatizada pelo:

Agendador de Tarefas do Windows

Configuração atual:

Frequência: diária

O Agendador executa:

atualizar_apol.py

O resultado da execução pode ser acompanhado através do arquivo:

logs/apol.log

Logs

O log registra:

início da execução;
quantidade de processos recebidos;
alterações realizadas;
resposta do APOL;
término da execução;
duração do processo;
erros encontrados.

Power BI

O dashboard está localizado em:

apol_BI/APOL_integracao.pbix

O Power BI utiliza os dados armazenados no SQLite.

A conexão foi configurada através de uma fonte de dados compatível com o ambiente local.

O fluxo de atualização é:

APOL
 ↓
SQLite atualizado
 ↓
Power BI
 ↓
Atualizar

A atualização do banco é automática. O Power BI Desktop precisa ser atualizado para carregar os dados modificados no banco.

Validação da integração

A integração foi testada em diferentes etapas:

comunicação com o Webservice;
autenticação;
recebimento dos processos;
transformação dos dados;
criação das tabelas SQLite;
criação das views;
atualização incremental;
sincronização dos IDs com o APOL;
execução automática pelo Windows;
geração de logs;
leitura dos dados pelo Power BI.

Tecnologias
Python
Requests
Pandas
SQLite
SQL
Power BI
DAX
PowerShell
Windows Task Scheduler
Webservice REST

Objetivo

O projeto tem como objetivo automatizar a extração e disponibilização de informações do APOL para análise no Power BI, reduzindo a necessidade de extração manual dos dados e criando uma estrutura de atualização controlada e rastreável.

Observações

Este projeto utiliza credenciais de acesso ao Webservice do APOL. Informações de autenticação, bancos locais e arquivos de configuração contendo dados sensíveis não devem ser publicados em repositórios públicos.

Para utilização em outro ambiente, será necessário configurar:

credenciais do APOL;
dependências Python;
banco SQLite;
conexão do Power BI;
Agendador de Tarefas.


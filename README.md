## Integração APOL → Power BI

Pipeline de integração desenvolvido em Python para consumo dos Webservices do APOL, transformação e persistência dos dados em SQLite, disponibilização para o Power BI e acompanhamento das movimentações processuais.

O projeto foi estruturado para realizar atualizações incrementais, atualização dos detalhes dos processos e execução automatizada por meio do Agendador de Tarefas do Windows.

## Objetivo

Automatizar a extração e disponibilização de informações do APOL para análise no Power BI, reduzindo a necessidade de extrações manuais e criando uma estrutura de atualização controlada, rastreável e reutilizável.

O projeto também permite analisar:

- quantidade de pedidos de marca por ano;
- situação dos processos;
- decisões de deferimento e indeferimento;
- índice de indeferimentos;
- prazo médio de decisão;
- prazo médio de deferimento;
- prazo médio de indeferimento;
- despachos e movimentações;
- ocorrências;
- providências;
- responsáveis pelas providências;
- timeline dos processos.

## Arquitetura
```
┌─────────────────────────────┐
│            APOL             │
│       Webservices API       │
│       REST + SOAP/WSDL      │
└──────────────┬──────────────┘
               │
               │ HTTP / JSON
               │ SOAP / XML
               ▼
┌─────────────────────────────┐
│           Python            │
│                             │
│ apol_client.py              │
│ apol_transform.py           │
│ apol_sync.py                │
│ apol_database.py            │
│ atualizar_apol.py           │
└──────────────┬──────────────┘
               │
               │ INSERT / UPDATE
               ▼
┌─────────────────────────────┐
│           SQLite            │
│                             │
│ processos                   │
│ processos_envolvidos        │
│ despachos                   │
│ ocorrencias                 │
│ providencias                │
└──────────────┬──────────────┘
               │
               │ Python / ODBC
               ▼
┌─────────────────────────────┐
│          Power BI           │
│                             │
│ APOL_integracao.pbix        │
│                             │
│ Indicadores                 │
│ Análises                    │
│ Timeline                    │
└─────────────────────────────┘
```
## Fluxo de atualização

O processo de atualização segue as seguintes etapas:
```
APOL
  ↓
Consulta de processos
  ↓
Transformação dos dados
  ↓
Atualização incremental
  ↓
SQLite
  ↓
Atualização dos detalhes
  ↓
Views
  ↓
Power BI
  ↓
Atualização dos indicadores
```
Etapas

1. O Python se conecta aos Webservices do APOL.
2. Os processos são consultados.
3. Os dados recebidos são transformados.
4. Os processos novos ou alterados são inseridos/atualizados no SQLite.
5. Os envolvidos são associados aos respectivos processos.
6. Os IDs sincronizados são enviados ao APOL quando aplicável.
7. Os detalhes dos processos são consultados.
8. Despachos, ocorrências e providências são atualizados.
9. A execução é registrada em log.
10. O Power BI utiliza o banco SQLite como fonte de dados.

## Estrutura do projeto
```
projeto2/
│
├── apol_client.py
├── apol_database.py
├── apol_sync.py
├── apol_transform.py
├── apol_views.py
├── atualizar_apol.py
├── powerbi_apol.py
│
├── apol_help.html
├── help_unificados.html
├── wsProcessoMarca.wsdl
│
├── tests/
│   ├── teste.py
│   └── teste_providencia.py
│
├── apol_BI/
│   └── APOL_integracao.pbix
│
├── .env
├── apol.db
└── README.md
```
Arquivos como ```.env```, ```apol.db``` e logs locais devem permanecer fora do versionamento público por meio do ```.gitignore```.

## Principais componentes

```apol_client.py```

Responsável pela comunicação com o Webservice do APOL.

Principais responsabilidades:

- autenticação;
- requisições à API;
- consulta de processos;
- tratamento de erros HTTP;
- validação das respostas;
- comunicação com os serviços disponibilizados pelo APOL.

```apol_transform.py```

Responsável pela transformação dos dados recebidos.

Os dados são organizados em estruturas adequadas para persistência no banco de dados.

Principais entidades:

- processos;
- processos e envolvidos.

```apol_sync.py```

Responsável pela preparação dos identificadores necessários para sincronização com o APOL.

São tratados diferentes grupos de processos:

- marcas;
- marcas internacionais;
- patentes;
- patentes internacionais.

```apol_database.py```

Responsável pelas operações de persistência no SQLite.

Entre suas responsabilidades estão:

- criação da estrutura do banco;
- inserção de registros;
- atualização de registros;
- UPSERT;
- armazenamento dos detalhes dos processos;
- atualização de despachos;
- atualização de ocorrências;
- atualização de providências.

```apol_views.py```

Responsável pela criação das views utilizadas para facilitar o consumo dos dados pelo Power BI.

Views principais:
```
vw_processos
vw_processos_envolvidos
vw_despachos
vw_ocorrencias
vw_providencias
```
```atualizar_apol.py```

É o principal script da automação.

Executa o fluxo de atualização:
```
Consultar APOL
      ↓
Transformar dados
      ↓
Salvar / atualizar SQLite
      ↓
Sincronizar IDs
      ↓
Atualizar detalhes
      ↓
Registrar execução
```
O processo utiliza UPSERT para atualizar registros existentes e inserir novos registros.

```powerbi_apol.py```

Script responsável pela disponibilização das diferentes estruturas de dados para consumo pelo Power BI. São carregadas estruturas relacionadas a:
```
df_processos
df_envolvidos
df_despachos
df_ocorrencias
df_providencias
```
## Banco de dados

O projeto utiliza SQLite como camada intermediária de persistência. Banco utilizado localmente:
```
apol.db
```
Tabela ```processos```

Armazena informações principais dos processos. Entre os campos estão:

- ID;
- número do processo;
- marca;
- classe;
- situação;
- titular;
- natureza;
- status;
- especificação;
- país de origem;
- data de depósito.

Tabela ```processos_envolvidos```

Relaciona processos aos seus respectivos envolvidos. Campos principais:
```
ProcessoId
EnvolvidoId
TipoEnvolvido
```
Tabela ```despachos```

Armazena movimentações e decisões publicadas relacionadas aos processos. Principais informações:
```
ProcessoId
RPI
DataRPI
Despacho
Descricao
Complemento
Pagina
```
Tabela ```ocorrencias```

Armazena ocorrências relacionadas aos processos. Principais informações:
```
ProcessoId
DataDeGeracao
Descricao
Protocolo
Detalhe
```
Tabela ```providencias```
Armazena providências gerenciais relacionadas aos processos. Principais informações:
```
ProcessoId
DataGerencial
DataOficial
Despacho
RPI
Descricao
Executada
ResponsavelNome
```
## Atualização incremental

A atualização dos processos utiliza UPSERT baseado no identificador:

```Id```

Quando um processo ainda não existe:

```INSERT```

Quando o processo já existe:

```UPDATE```

Essa abordagem evita a reconstrução completa do banco a cada execução.

Além disso, os detalhes dos processos são atualizados para manter informações de:

- despachos;
- ocorrências;
- providências.

## Power BI

O dashboard está localizado em:

```apol_BI/APOL_integracao.pbix```

O Power BI utiliza os dados armazenados no SQLite para construção das análises. O modelo foi estruturado para permitir o relacionamento entre:
```
Calendario
     │
     ▼
df_processos
     │
     ▼
Timeline
```
Além das tabelas relacionadas aos detalhes dos processos.

## Indicadores

O dashboard apresenta indicadores voltados à análise dos processos de registro de marcas.

Principais KPIs

- Pedidos de marca
- Índice de indeferimentos
- Prazo médio de decisão
- Prazo médio de deferimento
- Prazo médio de indeferimento

Também são apresentadas análises de:

- pedidos por ano;
- resultado das decisões do INPI;
- prazo médio por resultado;
- processos por classe;
- processos por situação.

## Análise das decisões

As movimentações do APOL são classificadas de acordo com o conteúdo dos despachos. As principais categorias utilizadas são:
```
Deferimento
Indeferimento
Outros
```
A análise considera os eventos relevantes para identificar o resultado final do processo. Para deferimentos, o projeto considera o despacho de concessão de registro como referência para o cálculo do prazo final. O prazo de decisão é calculado a partir da diferença entre:
```
Data de depósito
        ↓
Data da decisão
```
## Timeline dos Processos

Como funcionalidade adicional, foi criada uma tabela consolidada de eventos denominada:
```
Timeline
Ela reúne diferentes tipos de movimentações:
Depósito
Despacho
Ocorrência
Providência
```
A timeline permite acompanhar cronologicamente os eventos associados a cada processo. Também é possível filtrar os eventos por:

- número do processo;
- marca;
- tipo de movimentação;
- responsável pela providência.

## Responsáveis

As providências possuem informação de responsável por meio do campo:

```ResponsavelNome```

Esse campo é utilizado na Timeline para permitir a análise das providências associadas a cada responsável.

## Configuração das credenciais

As credenciais do APOL são armazenadas em um arquivo .env.

Exemplo:
```
APOL_USUARIO=seu_usuario
APOL_SENHA=sua_senha
```
O arquivo .env não deve ser publicado no GitHub.
Também não devem ser publicados:
```
.env
*.db
logs/
__pycache__/
```
## Dependências

Principais bibliotecas utilizadas:
```
requests
python-dotenv
pandas
```
Instalação:

```pip install requests python-dotenv pandas```

## Execução manual

Para executar uma atualização manual:

```py atualizar_apol.py```

Quando não existem novos processos ou alterações, a execução pode apresentar:
```
Processos recebidos: 0

Nenhum processo novo ou alterado.
Banco permanece inalterado.
```
Mesmo nesse cenário, os detalhes dos processos armazenados podem ser atualizados.

## Automação

A atualização pode ser executada automaticamente utilizando o:

Windows Task Scheduler — Agendador de Tarefas do Windows

O fluxo automatizado executa o script:

```atualizar_apol.py```

A configuração pode ser realizada para execução periódica, por exemplo:

```Frequência: diária```

Os resultados podem ser acompanhados pelos logs locais da aplicação.

## Logs

Os logs são utilizados para acompanhar a execução da integração. Entre as informações registradas estão:

- início da execução;
- quantidade de processos recebidos;
- processos inseridos;
- processos atualizados;
- atualização dos detalhes;
- resposta do APOL;
- duração da execução;
- erros encontrados.

## Testes

O projeto possui scripts de teste relacionados à integração e ao processamento das informações. Entre os cenários testados estão:

- comunicação com o Webservice;
- autenticação;
- recebimento dos processos;
- transformação dos dados;
- persistência no SQLite;
- atualização incremental;
- sincronização;
- atualização de providências;
- criação das views;
- consumo pelo Power BI.

## Validação da integração

A integração foi validada em diferentes etapas:
```
Webservice
    ↓
Autenticação
    ↓
Consulta
    ↓
Transformação
    ↓
SQLite
    ↓
Atualização incremental
    ↓
Detalhamento dos processos
    ↓
Views
    ↓
Power BI
```
Também foi validado o cenário de execução sem novos processos, garantindo que o banco não seja reconstruído desnecessariamente.

## Tecnologias

- Python
- Requests
- Pandas
- SQLite
- SQL
- Power BI
- DAX
- PowerShell
- SOAP
- REST
- XML
- JSON
- WSDL
- Windows Task Scheduler

## Arquivos de apoio

O projeto contém arquivos relacionados à documentação e integração com os serviços do APOL:
```
apol_help.html
help_unificados.html
wsProcessoMarca.wsdl
```
Esses arquivos auxiliam na compreensão dos serviços e estruturas utilizadas na integração.

## Segurança

Este projeto utiliza autenticação para acesso aos serviços do APOL. Por questões de segurança, credenciais, bancos locais, logs e informações de configuração não devem ser publicados em repositórios públicos.
```
.env
apol.db
logs/
```
estão devidamente protegidos pelo .gitignore.

## Resultado

O projeto demonstra a construção de um pipeline completo de dados:
```
             APOL
              │
              ▼
       Webservice / SOAP
              │
              ▼
           Python
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
 Transformação   Atualização
       │         Incremental
       └──────┬──────┘
              ▼
           SQLite
              │
              ▼
          Power BI
              │
       ┌──────┼──────────┐
       ▼      ▼          ▼
    KPIs   Análises   Timeline
```
A solução integra engenharia de dados, automação, banco de dados, análise e visualização, transformando dados operacionais do APOL em informações estruturadas para suporte à análise de processos de registro de marcas.

## Próximos passos

Possíveis evoluções do projeto:

- publicação do dashboard em ambiente Power BI Service;
- automação do refresh do Power BI;
- expansão dos indicadores;
- monitoramento automatizado das execuções;
- tratamento de novos tipos de processos;
- ampliação da análise histórica;
- integração com outras fontes de dados.

## Autor

Gustavo Evangelista

Projeto desenvolvido como aplicação prática de conhecimentos em:

Python · SQL · SQLite · Power BI · DAX · APIs · Automação · Análise de Dados

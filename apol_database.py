import sqlite3

from apol_client import ApolClient
from apol_transform import (
    transformar_processos,
    transformar_envolvidos
)


BANCO = "apol.db"

# Colunas que a tabela "processos" espera, na ordem da tabela.
# Usado tanto para garantir que existam no DataFrame quanto para
# montar os parâmetros nomeados do INSERT abaixo.
COLUNAS_PROCESSOS = [
    "Id",
    "NumeroDoProcesso",
    "Terceiro",
    "Natureza",
    "Especificacao",
    "Marca",
    "Classe",
    "Situacao",
    "Titular",
    "Pasta",
    "Referencia",
    "PaisDeOrigem",
    "Status"
]


def salvar_dados_incremental(dados):
    """
    Grava/atualiza processos e envolvidos no SQLite (UPSERT por Id).
    Esta é a única implementação de gravação do projeto;
    atualizar_apol.py chama esta função em vez de reimplementá-la.
    """

    df_processos = transformar_processos(dados)
    df_envolvidos = transformar_envolvidos(dados)

    if df_processos.empty:
        return 0, 0

    df_processos = df_processos.drop(
        columns=["Envolvidos"],
        errors="ignore"
    )

    # Garante que todas as colunas esperadas existem, mesmo que
    # algum processo específico não tenha vindo com todos os campos.
    for coluna in COLUNAS_PROCESSOS:
        if coluna not in df_processos.columns:
            df_processos[coluna] = None

    conexao = sqlite3.connect(BANCO)

    try:

        # Processos: parâmetros nomeados, não dependem da ordem
        # de colunas do DataFrame nem da ordem do to_sql.
        for _, linha in df_processos.iterrows():

            conexao.execute("""
                INSERT INTO processos (
                    Id,
                    NumeroDoProcesso,
                    Terceiro,
                    Natureza,
                    Especificacao,
                    Marca,
                    Classe,
                    Situacao,
                    Titular,
                    Pasta,
                    Referencia,
                    PaisDeOrigem,
                    Status
                )
                VALUES (
                    :Id, :NumeroDoProcesso, :Terceiro, :Natureza,
                    :Especificacao, :Marca, :Classe, :Situacao,
                    :Titular, :Pasta, :Referencia, :PaisDeOrigem,
                    :Status
                )

                ON CONFLICT(Id) DO UPDATE SET
                    NumeroDoProcesso = excluded.NumeroDoProcesso,
                    Terceiro = excluded.Terceiro,
                    Natureza = excluded.Natureza,
                    Especificacao = excluded.Especificacao,
                    Marca = excluded.Marca,
                    Classe = excluded.Classe,
                    Situacao = excluded.Situacao,
                    Titular = excluded.Titular,
                    Pasta = excluded.Pasta,
                    Referencia = excluded.Referencia,
                    PaisDeOrigem = excluded.PaisDeOrigem,
                    Status = excluded.Status
            """, linha[COLUNAS_PROCESSOS].to_dict())

        # Envolvidos
        for _, linha in df_envolvidos.iterrows():

            conexao.execute("""
                INSERT OR IGNORE INTO processos_envolvidos
                (
                    ProcessoId,
                    EnvolvidoId,
                    TipoEnvolvido
                )
                VALUES (?, ?, ?)
            """, (
                linha["ProcessoId"],
                linha["EnvolvidoId"],
                linha["TipoEnvolvido"]
            ))

        conexao.commit()

    finally:

        conexao.close()

    return len(df_processos), len(df_envolvidos)


def garantir_schema():
    """
    Cria as tabelas/colunas novas se ainda não existirem, sem apagar
    nada que já esteja no banco. Seguro de rodar toda vez.
    """

    conexao = sqlite3.connect(BANCO)

    try:

        colunas_processos = [
            linha[1]
            for linha in conexao.execute(
                "PRAGMA table_info(processos)"
            ).fetchall()
        ]

        if "DataDeDeposito" not in colunas_processos:
            conexao.execute(
                "ALTER TABLE processos ADD COLUMN DataDeDeposito TEXT"
            )

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS despachos (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                ProcessoId INTEGER NOT NULL,
                RPI TEXT,
                DataRPI TEXT,
                Despacho TEXT,
                Descricao TEXT,
                Complemento TEXT,
                Pagina TEXT,
                FOREIGN KEY (ProcessoId) REFERENCES processos(Id)
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS ocorrencias (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                ProcessoId INTEGER NOT NULL,
                DataDeGeracao TEXT,
                Descricao TEXT,
                Protocolo TEXT,
                Detalhe TEXT,
                FOREIGN KEY (ProcessoId) REFERENCES processos(Id)
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS providencias (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                ProcessoId INTEGER NOT NULL,
                DataGerencial TEXT,
                DataOficial TEXT,
                Despacho TEXT,
                RPI TEXT,
                Descricao TEXT,
                Executada BOOLEAN,
                ResponsavelNome TEXT,
                FOREIGN KEY (ProcessoId) REFERENCES processos(Id)
            )
        """)

        conexao.commit()

    finally:

        conexao.close()


def _como_lista(valor):
    """
    O parser de XML devolve dict quando há um único item repetido
    e list quando há vários. Isso normaliza para lista sempre,
    para o código de gravação não precisar tratar os dois casos.
    """

    if not valor:
        return []

    if isinstance(valor, list):
        return valor

    return [valor]


def salvar_detalhe_processo(id_processo, processo_detalhado):
    """
    Grava Data de Depósito, despachos, ocorrências e providências
    de UM processo, a partir do dict já desembrulhado retornado por
    ApolClient.extrair_response(cliente.consultar_processo_marca(...)).

    Faz "full refresh" de despachos/ocorrências/providências: apaga
    os registros antigos deste processo e insere os atuais, porque
    o APOL não fornece um ID estável para cada item individual.
    """

    garantir_schema()

    data_deposito = processo_detalhado.get("DataDeDeposito") or None

    despachos = _como_lista(
        (processo_detalhado.get("Despachos") or {}).get("DespachoMarcaDTO")
    )

    ocorrencias = _como_lista(
        (processo_detalhado.get("Ocorrencias") or {}).get("OcorrenciaDTO")
    )

    providencias = _como_lista(
        (processo_detalhado.get("Providencias") or {}).get("ProvidenciaDTO")
    )

    conexao = sqlite3.connect(BANCO)

    try:

        if data_deposito:
            conexao.execute(
                "UPDATE processos SET DataDeDeposito = ? WHERE Id = ?",
                (data_deposito, id_processo)
            )

        conexao.execute(
            "DELETE FROM despachos WHERE ProcessoId = ?",
            (id_processo,)
        )

        for despacho in despachos:
            conexao.execute("""
                INSERT INTO despachos (
                    ProcessoId, RPI, DataRPI, Despacho,
                    Descricao, Complemento, Pagina
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                id_processo,
                despacho.get("RPI"),
                despacho.get("DataRPI"),
                despacho.get("Despacho"),
                despacho.get("Descricao"),
                despacho.get("Complemento"),
                despacho.get("pagina") or despacho.get("Pagina")
            ))

        conexao.execute(
            "DELETE FROM ocorrencias WHERE ProcessoId = ?",
            (id_processo,)
        )

        for ocorrencia in ocorrencias:
            conexao.execute("""
                INSERT INTO ocorrencias (
                    ProcessoId, DataDeGeracao, Descricao,
                    Protocolo, Detalhe
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                id_processo,
                ocorrencia.get("DataDeGeracao"),
                ocorrencia.get("Descricao"),
                ocorrencia.get("Protocolo"),
                ocorrencia.get("Detalhe")
            ))

        conexao.execute(
            "DELETE FROM providencias WHERE ProcessoId = ?",
            (id_processo,)
        )

        for providencia in providencias:

            responsavel = providencia.get("Responsavel") or {}

            conexao.execute("""
                INSERT INTO providencias (
                    ProcessoId, DataGerencial, DataOficial, Despacho,
                    RPI, Descricao, Executada, ResponsavelNome
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_processo,
                providencia.get("DataGerencial"),
                providencia.get("DataOficial"),
                providencia.get("Despacho"),
                providencia.get("RPI"),
                providencia.get("Descricao"),
                providencia.get("Executada"),
                responsavel.get("Nome")
            ))

        conexao.commit()

    finally:

        conexao.close()

    return {
        "despachos": len(despachos),
        "ocorrencias": len(ocorrencias),
        "providencias": len(providencias)
    }


if __name__ == "__main__":

    cliente = ApolClient()

    dados = cliente.obter_processos_unificados()

    print("=" * 60)
    print("TESTE DE GRAVAÇÃO INCREMENTAL")
    print("=" * 60)

    print("\nProcessos recebidos:")
    print(dados.get("Quantidade"))

    processos, envolvidos = salvar_dados_incremental(dados)

    print("\nProcessos processados:", processos)
    print("Envolvidos processados:", envolvidos)
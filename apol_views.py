import sqlite3


BANCO = "apol.db"


conexao = sqlite3.connect(BANCO)

try:

    # Remove as views existentes para recriá-las corretamente
    conexao.execute("DROP VIEW IF EXISTS vw_processos")
    conexao.execute("DROP VIEW IF EXISTS vw_processos_envolvidos")
    conexao.execute("DROP VIEW IF EXISTS vw_despachos")
    conexao.execute("DROP VIEW IF EXISTS vw_ocorrencias")
    conexao.execute("DROP VIEW IF EXISTS vw_providencias")

    # ==========================================================
    # PROCESSOS
    # ==========================================================

    conexao.execute("""
        CREATE VIEW vw_processos AS
        SELECT
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
            Status,
            DataDeDeposito
        FROM processos
    """)

    # ==========================================================
    # ENVOLVIDOS
    # ==========================================================

    conexao.execute("""
        CREATE VIEW vw_processos_envolvidos AS
        SELECT
            ProcessoId,
            EnvolvidoId,
            TipoEnvolvido
        FROM processos_envolvidos
    """)

    # ==========================================================
    # DESPACHOS
    # ==========================================================

    conexao.execute("""
        CREATE VIEW vw_despachos AS
        SELECT
            Id,
            ProcessoId,
            RPI,
            DataRPI,
            Despacho,
            Descricao,
            Complemento,
            Pagina
        FROM despachos
    """)

    # ==========================================================
    # OCORRÊNCIAS
    # ==========================================================

    conexao.execute("""
        CREATE VIEW vw_ocorrencias AS
        SELECT
            Id,
            ProcessoId,
            DataDeGeracao,
            Descricao,
            Protocolo,
            Detalhe
        FROM ocorrencias
    """)

    # ==========================================================
    # PROVIDÊNCIAS
    # ==========================================================

    conexao.execute("""
        CREATE VIEW vw_providencias AS
        SELECT
            Id,
            ProcessoId,
            DataGerencial,
            DataOficial,
            Despacho,
            RPI,
            Descricao,
            Executada,
            ResponsavelNome
        FROM providencias
    """)

    conexao.commit()

    print("=" * 60)
    print("VIEWS APOL")
    print("=" * 60)

    print("\nViews criadas:")
    print("- vw_processos")
    print("- vw_processos_envolvidos")
    print("- vw_despachos")
    print("- vw_ocorrencias")
    print("- vw_providencias")

finally:

    conexao.close()
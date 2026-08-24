import sqlite3


BANCO = "apol.db"


conexao = sqlite3.connect(BANCO)

try:

    conexao.execute("""
        CREATE VIEW IF NOT EXISTS vw_processos AS
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
            Status
        FROM processos
    """)

    conexao.execute("""
        CREATE VIEW IF NOT EXISTS vw_processos_envolvidos AS
        SELECT
            ProcessoId,
            EnvolvidoId,
            TipoEnvolvido
        FROM processos_envolvidos
    """)

    conexao.commit()

    print("=" * 60)
    print("VIEWS APOL")
    print("=" * 60)

    print("\nViews criadas:")
    print("- vw_processos")
    print("- vw_processos_envolvidos")

finally:

    conexao.close()
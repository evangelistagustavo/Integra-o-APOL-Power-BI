import sqlite3


BANCO = "apol.db"


conexao = sqlite3.connect(BANCO)

try:

    cursor = conexao.cursor()

    print("=" * 60)
    print("VALIDAÇÃO DO BANCO APOL")
    print("=" * 60)

    # Tabelas
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    tabelas = cursor.fetchall()

    print("\nTabelas:")

    for tabela in tabelas:
        print("-", tabela[0])

    # Processos
    cursor.execute(
        "SELECT COUNT(*) FROM processos"
    )

    quantidade_processos = cursor.fetchone()[0]

    print(
        "\nProcessos:",
        quantidade_processos
    )

    # Envolvidos
    cursor.execute(
        "SELECT COUNT(*) FROM processos_envolvidos"
    )

    quantidade_envolvidos = cursor.fetchone()[0]

    print(
        "Envolvidos:",
        quantidade_envolvidos
    )

    # Primeiro processo
    cursor.execute("""
        SELECT
            Id,
            NumeroDoProcesso,
            Marca,
            Classe,
            Situacao,
            Titular
        FROM processos
        LIMIT 1
    """)

    processo = cursor.fetchone()

    print("\nPrimeiro processo:")

    print(processo)

finally:

    conexao.close()
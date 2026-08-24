import sqlite3
import pandas as pd


BANCO = "apol.db"


df_processos = pd.read_csv(
    "processos.csv",
    dtype={
        "NumeroDoProcesso": str
    }
)

conexao = sqlite3.connect(BANCO)

try:

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS processos (
            Id INTEGER PRIMARY KEY,
            NumeroDoProcesso TEXT,
            Terceiro BOOLEAN,
            Natureza TEXT,
            Especificacao TEXT,
            Marca TEXT,
            Classe TEXT,
            Situacao TEXT,
            Titular TEXT,
            Pasta TEXT,
            Referencia TEXT,
            PaisDeOrigem TEXT,
            Status TEXT
        )
    """)

    df_processos.to_sql(
        "processos",
        conexao,
        if_exists="append",
        index=False
    )

    conexao.commit()

    print("=" * 60)
    print("BANCO RECONSTRUÍDO")
    print("=" * 60)

    print(
        "\nProcessos inseridos:",
        len(df_processos)
    )

finally:

    conexao.close()
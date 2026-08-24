import sqlite3
import pandas as pd


BANCO = "apol.db"


df = pd.read_csv(
    "processos.csv",
    dtype={
        "NumeroDoProcesso": str
    }
)

conexao = sqlite3.connect(BANCO)

try:

    print("=" * 60)
    print("TESTE UPSERT")
    print("=" * 60)

    for _, linha in df.iterrows():

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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

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
        """, tuple(linha))

    conexao.commit()

    cursor = conexao.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM processos"
    )

    total = cursor.fetchone()[0]

    print("\nRegistros no banco após UPSERT:", total)

finally:

    conexao.close()
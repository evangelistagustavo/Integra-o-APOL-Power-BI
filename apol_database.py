import sqlite3

from apol_client import ApolClient
from apol_transform import (
    transformar_processos,
    transformar_envolvidos
)


BANCO = "apol.db"


def salvar_dados_incremental(dados):

    df_processos = transformar_processos(dados)
    df_envolvidos = transformar_envolvidos(dados)

    if df_processos.empty:
        return 0, 0

    df_processos = df_processos.drop(
        columns=["Envolvidos"],
        errors="ignore"
    )

    conexao = sqlite3.connect(BANCO)

    try:

        # Processos
        df_processos.to_sql(
            "processos_novos",
            conexao,
            if_exists="replace",
            index=False
        )

        conexao.execute("""
            INSERT INTO processos
            SELECT *
            FROM processos_novos
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
        """)

        conexao.execute(
            "DROP TABLE processos_novos"
        )

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
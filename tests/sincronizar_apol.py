import sqlite3

from apol_client import ApolClient
from apol_transform import (
    transformar_processos,
    transformar_envolvidos
)
from apol_sync import obter_ids_sincronizacao


BANCO = "apol.db"


def salvar_dados(dados):

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

        for _, linha in df_envolvidos.iterrows():

            conexao.execute("""
                INSERT OR IGNORE INTO processos_envolvidos (
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


def existem_processos(dados):

    return any([
        dados.get("ProcessosMarca"),
        dados.get("ProcessosMarcaInternacional"),
        dados.get("ProcessosPatente"),
        dados.get("ProcessosPatenteInternacional")
    ])


if __name__ == "__main__":

    print("=" * 60)
    print("SINCRONIZAÇÃO APOL")
    print("=" * 60)

    cliente = ApolClient()

    # ========================================================
    # 1. OBTÉM PROCESSOS DO APOL
    # ========================================================

    dados = cliente.obter_processos_unificados()

    print("\nProcessos recebidos:")
    print(dados.get("Quantidade"))

    # ========================================================
    # 2. VERIFICA SE EXISTEM PROCESSOS
    # ========================================================

    if not existem_processos(dados):

        print("\nNenhum processo novo ou alterado.")
        print("Nada para sincronizar.")

        exit()

    # ========================================================
    # 3. SALVA OS DADOS NO BANCO
    # ========================================================

    processos, envolvidos = salvar_dados(dados)

    print("\nDados salvos no banco:")
    print("Processos:", processos)
    print("Envolvidos:", envolvidos)

    # ========================================================
    # 4. OBTÉM OS IDs PARA SINCRONIZAÇÃO
    # ========================================================

    ids = obter_ids_sincronizacao(dados)

    print("\nIDs preparados para sincronização:")

    print(
        "Marcas:",
        len(ids["MarcasIds"])
    )

    print(
        "Marcas internacionais:",
        len(ids["MarcasInternacionalId"])
    )

    print(
        "Patentes:",
        len(ids["PatentesId"])
    )

    print(
        "Patentes internacionais:",
        len(ids["PatentesInternacionalId"])
    )

    # ========================================================
    # 5. INFORMA A SINCRONIZAÇÃO AO APOL
    # ========================================================

    resposta = cliente.informar_sincronizacao(ids)

    print("\nResposta do APOL:")
    print(resposta)

    # ========================================================
    # 6. CONFIRMA RESULTADO
    # ========================================================

    if resposta.get("Sucesso"):

        print("\nSINCRONIZAÇÃO CONCLUÍDA.")

    else:

        print(
            "\nATENÇÃO: "
            "o APOL não confirmou a sincronização."
        )
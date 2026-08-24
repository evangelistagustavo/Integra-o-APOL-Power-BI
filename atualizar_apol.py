import sqlite3
from datetime import datetime

from apol_client import ApolClient
from apol_transform import (
    transformar_processos,
    transformar_envolvidos
)
from apol_sync import obter_ids_sincronizacao


BANCO = "apol.db"


def existem_processos(dados):

    return any([
        dados.get("ProcessosMarca"),
        dados.get("ProcessosMarcaInternacional"),
        dados.get("ProcessosPatente"),
        dados.get("ProcessosPatenteInternacional")
    ])


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


if __name__ == "__main__":

    inicio = datetime.now()

    print("=" * 60)
    print("ATUALIZAÇÃO APOL")
    print("=" * 60)

    print(
        "\nInício:",
        inicio.strftime("%d/%m/%Y %H:%M:%S")
    )

    try:

        # 1. Conecta ao APOL
        cliente = ApolClient()

        # 2. Obtém processos
        dados = cliente.obter_processos_unificados()

        quantidade = dados.get("Quantidade")

        print("\nProcessos recebidos:")
        print(quantidade)

        # 3. Verifica se existem processos
        if not existem_processos(dados):

            print("\nNenhum processo novo ou alterado.")
            print("Banco permanece inalterado.")

        else:

            # 4. Salva os dados
            processos, envolvidos = salvar_dados(dados)

            print("\nProcessos processados:")
            print(processos)

            print("Envolvidos processados:")
            print(envolvidos)

            # 5. Obtém IDs para sincronização
            ids = obter_ids_sincronizacao(dados)

            print("\nIDs preparados para sincronização:")
            print("Marcas:", len(ids["MarcasIds"]))
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

            # 6. Confirma sincronização
            resposta = cliente.informar_sincronizacao(ids)

            print("\nResposta do APOL:")
            print(resposta)

            if resposta.get("Sucesso"):

                print("\nATUALIZAÇÃO CONCLUÍDA.")

            else:

                print(
                    "\nATENÇÃO: "
                    "o APOL não confirmou a sincronização."
                )

    except Exception as erro:

        print("\nERRO NA ATUALIZAÇÃO:")
        print(erro)

    finally:

        fim = datetime.now()

        print(
            "\nFim:",
            fim.strftime("%d/%m/%Y %H:%M:%S")
        )

        print(
            "Duração:",
            fim - inicio
        )
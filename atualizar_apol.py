import sqlite3
from datetime import datetime

from apol_client import ApolClient
from apol_database import (
    BANCO,
    salvar_dados_incremental,
    salvar_detalhe_processo
)
from apol_sync import obter_ids_sincronizacao


def existem_processos(dados):

    return any([
        dados.get("ProcessosMarca"),
        dados.get("ProcessosMarcaInternacional"),
        dados.get("ProcessosPatente"),
        dados.get("ProcessosPatenteInternacional")
    ])


def atualizar_detalhes_processos(cliente):
    """
    Busca o detalhe completo (Consultar Processo, via SOAP) de
    TODOS os processos de marca ja salvos no banco, e grava
    deposito, despachos, ocorrencias e providencias de cada um.

    Roda em toda atualizacao, independente de ter havido
    processo novo/alterado no endpoint unificado, para manter
    o dashboard sempre com o detalhe completo em dia.

    Processos com erro sao pulados (log no console) sem
    interromper os demais.
    """

    conexao = sqlite3.connect(BANCO)

    try:
        processos = conexao.execute(
            "SELECT Id, NumeroDoProcesso FROM processos "
            "WHERE NumeroDoProcesso IS NOT NULL "
            "AND NumeroDoProcesso != ''"
        ).fetchall()
    finally:
        conexao.close()

    sucesso = 0
    falha = 0

    for id_processo, numero_processo in processos:

        try:

            bruto = cliente.consultar_processo_marca(
                numero_processo
            )
            detalhe = ApolClient.extrair_response(bruto)

            salvar_detalhe_processo(id_processo, detalhe)

            sucesso += 1

        except Exception as erro:

            falha += 1

            print(
                f"  [detalhe] Falha no processo "
                f"{numero_processo} (Id {id_processo}): {erro}"
            )

    return sucesso, falha


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
            processos, envolvidos = salvar_dados_incremental(dados)

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

        # 7. Atualiza o detalhe completo (depósito, despachos,
        # ocorrências e providências) de TODOS os processos de
        # marca já salvos, para o dashboard ficar sempre em dia.
        # Roda sempre, mesmo sem processo novo/alterado no passo 3.
        print("\n" + "=" * 60)
        print("ATUALIZANDO DETALHE DOS PROCESSOS DE MARCA")
        print("=" * 60)

        sucesso_detalhe, falha_detalhe = atualizar_detalhes_processos(
            cliente
        )

        print("\nDetalhes atualizados com sucesso:", sucesso_detalhe)
        print("Detalhes com falha:", falha_detalhe)

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
import pandas as pd

from apol_client import ApolClient


def transformar_processos(dados):

    processos = dados.get("ProcessosMarca", [])

    df_processos = pd.DataFrame(processos)

    # Campos que devem permanecer como texto
    campos_texto = [
        "NumeroDoProcesso",
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

    for campo in campos_texto:

        if campo in df_processos.columns:
            df_processos[campo] = (
                df_processos[campo]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df_processos


def transformar_envolvidos(dados):

    processos = dados.get("ProcessosMarca", [])

    registros = []

    for processo in processos:

        processo_id = processo.get("Id")

        for envolvido in processo.get("Envolvidos", []):

            registros.append({
                "ProcessoId": processo_id,
                "EnvolvidoId": envolvido.get("Id"),
                "TipoEnvolvido": envolvido.get(
                    "TipoDoEnvolvidoNome"
                )
            })

    return pd.DataFrame(registros)


if __name__ == "__main__":

    cliente = ApolClient()

    dados = cliente.obter_processos_unificados()

    df_processos = transformar_processos(dados)
    df_envolvidos = transformar_envolvidos(dados)

    print("=" * 60)
    print("TRANSFORMAÇÃO DOS DADOS APOL")
    print("=" * 60)

    print("\nProcessos:")
    print(df_processos.shape)

    print("\nTipos:")
    print(df_processos.dtypes)

    print("\nEnvolvidos:")
    print(df_envolvidos.shape)

    print("\nPrimeiro processo:")
    print(df_processos.iloc[0].to_dict())
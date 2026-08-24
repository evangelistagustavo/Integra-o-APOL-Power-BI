import requests
import os
import json
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

usuario = os.getenv("APOL_USUARIO")
senha = os.getenv("APOL_SENHA")

url = (
    "https://ld2.ldsoft.com.br/"
    "webservices/apol/api/externo/"
    "processosunificados/ObterProcessosUnificados"
)


# ============================================================
# CONSULTA
# ============================================================

response = requests.get(
    url,
    auth=(usuario, senha),
    timeout=60
)


print("=" * 60)
print("TESTE - PROCESSOS UNIFICADOS APOL")
print("=" * 60)

print("Status HTTP:", response.status_code)


# ============================================================
# TRATAMENTO DA RESPOSTA
# ============================================================

if response.status_code == 200:

    dados = response.json()

    print("\nAutorizado:", dados.get("Autorizado"))
    print("Sucesso:", dados.get("Sucesso"))
    print("Quantidade:", dados.get("Quantidade"))

    print("\nChaves retornadas pela API:")

    for chave in dados.keys():
        print(" -", chave)


    # ========================================================
    # PROCESSOS DE MARCA
    # ========================================================

    processos_marca = dados.get("ProcessosMarca", [])

    print("\nProcessos de marca:", len(processos_marca))


    # ========================================================
    # OUTROS TIPOS DE PROCESSO
    # ========================================================

    processos_marca_internacional = dados.get(
        "ProcessosMarcaInternacional",
        []
    )

    processos_patente = dados.get(
        "ProcessosPatente",
        []
    )

    processos_patente_internacional = dados.get(
        "ProcessosPatenteInternacional",
        []
    )

    print(
        "Processos de marca internacional:",
        len(processos_marca_internacional)
    )

    print(
        "Processos de patente:",
        len(processos_patente)
    )

    print(
        "Processos de patente internacional:",
        len(processos_patente_internacional
        )
    )


    # ========================================================
    # PRIMEIRO PROCESSO DE MARCA
    # ========================================================

    if processos_marca:

        print("\n" + "=" * 60)
        print("PRIMEIRO PROCESSO DE MARCA")
        print("=" * 60)

        print(
            json.dumps(
                processos_marca[0],
                indent=4,
                ensure_ascii=False
            )
        )


    # ========================================================
    # SALVAR RESPOSTA COMPLETA
    # ========================================================

    with open(
        "resposta_processos_unificados.json",
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    print("\nResposta completa salva em:")
    print("resposta_processos_unificados.json")


else:

    print("\nErro na requisição:")
    print(response.text)
import requests
import os
from dotenv import load_dotenv

load_dotenv()

usuario = os.getenv("APOL_USUARIO")
senha = os.getenv("APOL_SENHA")

url = "https://ld2.ldsoft.com.br/webservices/apol/api/externo/processosunificados/ObterProcessosUnificados"

response = requests.get(
    url,
    auth=(usuario, senha)
)

print("Status HTTP:", response.status_code)

if response.status_code == 200:

    dados = response.json()

    print("Autorizado:", dados.get("Autorizado"))
    print("Sucesso:", dados.get("Sucesso"))
    print("Quantidade:", dados.get("Quantidade"))

    processos = dados.get("ProcessosMarca", [])

    print("Processos de marca:", len(processos))

    print("\nPrimeiro processo:")

    if processos:
        print(processos[0])

else:
    print("Erro na requisição:")
    print(response.text)
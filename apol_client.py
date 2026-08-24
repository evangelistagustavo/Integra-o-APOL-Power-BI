import os
import requests
from dotenv import load_dotenv


class ApolClient:

    BASE_URL = (
        "https://ld2.ldsoft.com.br/"
        "webservices/apol/api/externo"
    )

    def __init__(self):
        load_dotenv()

        self.usuario = os.getenv("APOL_USUARIO")
        self.senha = os.getenv("APOL_SENHA")

        if not self.usuario or not self.senha:
            raise ValueError(
                "APOL_USUARIO e APOL_SENHA "
                "não foram encontrados no arquivo .env."
            )

        self.session = requests.Session()

        self.session.auth = (
            self.usuario,
            self.senha
        )

        self.session.headers.update({
            "Accept": "application/json"
        })

    def obter_processos_unificados(self):

        endpoint = (
            f"{self.BASE_URL}/"
            "processosunificados/"
            "ObterProcessosUnificados"
        )

        try:

            response = self.session.get(
                endpoint,
                timeout=60
            )

            response.raise_for_status()

        except requests.exceptions.Timeout as erro:

            raise RuntimeError(
                "O APOL demorou muito para responder."
            ) from erro

        except requests.exceptions.ConnectionError as erro:

            raise RuntimeError(
                "Não foi possível conectar ao Webservice do APOL."
            ) from erro

        except requests.exceptions.HTTPError as erro:

            raise RuntimeError(
                f"Erro HTTP {response.status_code} "
                f"ao consultar o APOL: "
                f"{response.text[:500]}"
            ) from erro

        except requests.exceptions.RequestException as erro:

            raise RuntimeError(
                f"Erro na comunicação com o APOL: {erro}"
            ) from erro

        try:

            dados = response.json()

        except ValueError as erro:

            raise RuntimeError(
                "O APOL retornou uma resposta que "
                "não está em formato JSON."
            ) from erro

        if not dados.get("Autorizado", False):

            raise RuntimeError(
                "O APOL não autorizou a requisição."
            )

        if not dados.get("Sucesso", False):

            mensagem = (
                dados.get("Message")
                or dados.get("Mensagens")
                or "Erro não especificado pelo APOL."
            )

            raise RuntimeError(
                f"O APOL retornou Sucesso=False: {mensagem}"
            )

        return dados

    def informar_sincronizacao(self, ids):

        endpoint = (
            f"{self.BASE_URL}/"
            "processosunificados/"
            "InformarSincronizacaoProcessoUnificado"
        )

        payload = {
            "MarcasIds": ids.get("MarcasIds", []),
            "MarcasInternacionalId": ids.get(
                "MarcasInternacionalId", []
            ),
            "PatentesId": ids.get("PatentesId", []),
            "PatentesInternacionalId": ids.get(
                "PatentesInternacionalId", []
            )
        }

        try:

            response = self.session.post(
                endpoint,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

        except requests.exceptions.RequestException as erro:

            raise RuntimeError(
                f"Erro ao informar sincronização ao APOL: {erro}"
            ) from erro

        try:

            return response.json()

        except ValueError:

            return {
                "StatusHTTP": response.status_code,
                "Resposta": response.text
            }

    def resumo_processos(self, dados):

        return {
            "quantidade": dados.get("Quantidade"),

            "marcas": len(
                dados.get("ProcessosMarca", [])
            ),

            "marcas_internacionais": len(
                dados.get("ProcessosMarcaInternacional", [])
            ),

            "patentes": len(
                dados.get("ProcessosPatente", [])
            ),

            "patentes_internacionais": len(
                dados.get("ProcessosPatenteInternacional", [])
            )
        }


if __name__ == "__main__":

    print("=" * 60)
    print("TESTE DO APOL CLIENT")
    print("=" * 60)

    try:

        cliente = ApolClient()

        dados = cliente.obter_processos_unificados()

        resumo = cliente.resumo_processos(dados)

        print("\nConsulta realizada com sucesso.")

        print(
            "\nQuantidade informada pelo APOL:",
            resumo["quantidade"]
        )

        print(
            "Processos de marca:",
            resumo["marcas"]
        )

        print(
            "Processos de marca internacional:",
            resumo["marcas_internacionais"]
        )

        print(
            "Processos de patente:",
            resumo["patentes"]
        )

        print(
            "Processos de patente internacional:",
            resumo["patentes_internacionais"]
        )

    except Exception as erro:

        print("\nERRO:")
        print(erro)
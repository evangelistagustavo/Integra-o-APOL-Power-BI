import os
import re
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv


class ApolClient:

    BASE_URL = (
        "https://ld2.ldsoft.com.br/"
        "webservices/apol/api/externo"
    )

    # Endpoint SOAP (ASMX) de Processos de Marca (manual, seção 3).
    # Diferente do BASE_URL acima: este é SOAP, não REST/JSON.
    SOAP_PROCESSO_MARCA_URL = (
        "https://ld2.ldsoft.com.br/"
        "webservices/wsProcessos/wsProcessoMarca.asmx"
    )

    # Namespace confirmado no WSDL real (targetNamespace).
    # Repare na barra dupla no final: é assim mesmo no servidor.
    SOAP_NAMESPACE = "http://ld2.ldsoft.com.br//"

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

    def consultar_processo_marca(self, numero_processo):
        """
        Consulta um processo de Marca via SOAP
        (wsProcessoMarca.asmx / Consultar Processo - manual seção 3.1.1).

        Diferente de obter_processos_unificados, este endpoint traz
        os campos completos: DataDeDeposito, Despacho, Ocorrências,
        Providências, etc.

        Retorna um dict "cru" com a estrutura do XML de resposta
        (tags repetidas viram listas). O mapeamento para os nomes
        de campo definitivos deve ser ajustado depois de ver uma
        resposta real, comparando com o manual.
        """

        if not numero_processo:
            raise ValueError(
                "O número do processo deve ser informado."
            )

        soap_action = f"{self.SOAP_NAMESPACE}ConsultarProcesso"

        envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <ConsultarProcesso xmlns="{self.SOAP_NAMESPACE}">
      <usuario>{self.usuario}</usuario>
      <senha>{self.senha}</senha>
      <numeroDoProcesso>{numero_processo}</numeroDoProcesso>
    </ConsultarProcesso>
  </soap:Body>
</soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": soap_action
        }

        try:

            response = requests.post(
                self.SOAP_PROCESSO_MARCA_URL,
                data=envelope.encode("utf-8"),
                headers=headers,
                timeout=60
            )

            response.raise_for_status()

        except requests.exceptions.Timeout as erro:

            raise RuntimeError(
                "O APOL demorou muito para responder "
                "(Consultar Processo)."
            ) from erro

        except requests.exceptions.ConnectionError as erro:

            raise RuntimeError(
                "Não foi possível conectar ao Webservice "
                "wsProcessoMarca.asmx."
            ) from erro

        except requests.exceptions.HTTPError as erro:

            raise RuntimeError(
                f"Erro HTTP {response.status_code} "
                f"ao consultar processo de marca: "
                f"{response.text[:500]}"
            ) from erro

        except requests.exceptions.RequestException as erro:

            raise RuntimeError(
                f"Erro na comunicação com wsProcessoMarca.asmx: "
                f"{erro}"
            ) from erro

        return self._parse_soap_response(response.text)

    @staticmethod
    def extrair_response(dados_brutos):
        """
        Desembrulha o retorno de consultar_processo_marca até o dict
        com os campos do processo (DataDeDeposito, Despachos,
        Ocorrencias, Providencias, etc.), pulando os wrappers
        ConsultarProcessoResult/Response do SOAP.
        """

        try:
            return dados_brutos["ConsultarProcessoResult"]["Response"]
        except (KeyError, TypeError) as erro:
            raise RuntimeError(
                "Estrutura de resposta inesperada do "
                "Consultar Processo (SOAP): "
                f"{dados_brutos}"
            ) from erro

    @staticmethod
    def _strip_namespace(tag):
        """Remove o namespace de uma tag XML (ex: '{ns}Tag' -> 'Tag')."""
        return re.sub(r"^\{.*\}", "", tag)

    # Campos binários volumosos que não interessam para o dashboard.
    # Se precisar do conteúdo no futuro, remova o nome daqui.
    CAMPOS_BINARIOS_IGNORADOS = {"PDF", "AvisoPipeline", "Arquivo"}

    @classmethod
    def _xml_element_to_dict(cls, elemento):
        """
        Converte um elemento XML em dict/lista de forma genérica,
        sem depender de conhecer o schema exato de antemão.
        Tags repetidas dentro do mesmo pai viram lista.
        Campos binários volumosos (PDF, imagens) são substituídos
        por um marcador, para não poluir a resposta.
        """

        filhos = list(elemento)

        if not filhos:
            return (elemento.text or "").strip()

        resultado = {}

        for filho in filhos:

            nome = cls._strip_namespace(filho.tag)

            if nome in cls.CAMPOS_BINARIOS_IGNORADOS:
                texto = filho.text or ""
                valor = f"<binario omitido, {len(texto)} chars>" if texto else ""
            else:
                valor = cls._xml_element_to_dict(filho)

            if nome in resultado:

                if not isinstance(resultado[nome], list):
                    resultado[nome] = [resultado[nome]]

                resultado[nome].append(valor)

            else:
                resultado[nome] = valor

        return resultado

    @classmethod
    def _parse_soap_response(cls, xml_texto):
        """
        Faz o parsing da resposta SOAP e retorna o conteúdo
        do soap:Body como dict. Levanta RuntimeError se a
        resposta contiver um soap:Fault.
        """

        try:
            raiz = ET.fromstring(xml_texto)
        except ET.ParseError as erro:
            raise RuntimeError(
                "A resposta do APOL não é um XML válido: "
                f"{xml_texto[:500]}"
            ) from erro

        body = None

        for elemento in raiz:
            if cls._strip_namespace(elemento.tag) == "Body":
                body = elemento
                break

        if body is None or len(body) == 0:
            raise RuntimeError(
                "Resposta SOAP sem conteúdo em soap:Body."
            )

        conteudo = body[0]

        if cls._strip_namespace(conteudo.tag) == "Fault":
            fault_dict = cls._xml_element_to_dict(conteudo)
            raise RuntimeError(
                f"O APOL retornou um SOAP Fault: {fault_dict}"
            )

        return cls._xml_element_to_dict(conteudo)

    def obter_processo_por_id(self, id_processo):

        """
        Consulta o detalhamento de um processo pelo ID.

        IMPORTANTE:
        A rota exata deste método ainda será validada
        contra o endpoint disponibilizado pelo APOL.
        """

        if not id_processo:
            raise ValueError(
                "O ID do processo deve ser informado."
            )

        # A rota será definida após a validação
        # do endpoint específico do Webservice.
        raise NotImplementedError(
            "Endpoint de consulta por ID ainda não validado."
        )

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

    # Teste manual do endpoint SOAP de Marca (Consultar Processo).
    # Troque NUMERO_DO_PROCESSO por um processo real do APOL de vocês.
    NUMERO_DO_PROCESSO_TESTE = None  # ex: "123456789"

    if NUMERO_DO_PROCESSO_TESTE:

        print("\n" + "=" * 60)
        print("TESTE: CONSULTAR PROCESSO DE MARCA (SOAP)")
        print("=" * 60)

        try:

            cliente = ApolClient()

            resultado = cliente.consultar_processo_marca(
                NUMERO_DO_PROCESSO_TESTE
            )

            print("\nResposta (estrutura crua do XML):")
            print(resultado)

        except Exception as erro:

            print("\nERRO:")
            print(erro)
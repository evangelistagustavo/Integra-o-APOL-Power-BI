import os
import requests
from dotenv import load_dotenv

load_dotenv()

usuario = os.getenv("APOL_USUARIO")
senha = os.getenv("APOL_SENHA")

url = "http://ld2.ldsoft.com.br/webservices/wsProvidenciasApol/wsProvidencia.asmx"

soap = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">

    <soap:Header>
        <UsuarioSoapHeader xmlns="http://ld2.ldsoft.com.br/">
            <Usuario>{usuario}</Usuario>
            <Senha>{senha}</Senha>
        </UsuarioSoapHeader>
    </soap:Header>

    <soap:Body>
        <ObterProvidenciaPorProcesso xmlns="http://ld2.ldsoft.com.br/">
            <numeroProcesso>933332742</numeroProcesso>
        </ObterProvidenciaPorProcesso>
    </soap:Body>

</soap:Envelope>
"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "http://ld2.ldsoft.com.br/ObterProvidenciaPorProcesso"
}

print("=" * 60)
print("TESTE WEBSERVICE DE PROVIDÊNCIAS APOL")
print("=" * 60)

try:

    resposta = requests.post(
        url,
        data=soap.encode("utf-8"),
        headers=headers,
        timeout=60
    )

    print("\nHTTP:", resposta.status_code)

    print("\nResposta:")
    print(resposta.text[:10000])

except requests.exceptions.RequestException as erro:

    print("\nERRO DE COMUNICAÇÃO:")
    print(erro)

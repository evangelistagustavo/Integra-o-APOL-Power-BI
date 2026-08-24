def obter_ids_sincronizacao(dados):

    ids = {
        "MarcasIds": [],
        "MarcasInternacionalId": [],
        "PatentesId": [],
        "PatentesInternacionalId": []
    }

    for processo in dados.get("ProcessosMarca", []):
        if processo.get("Id"):
            ids["MarcasIds"].append(processo["Id"])

    for processo in dados.get("ProcessosMarcaInternacional", []):
        if processo.get("Id"):
            ids["MarcasInternacionalId"].append(
                processo["Id"]
            )

    for processo in dados.get("ProcessosPatente", []):
        if processo.get("Id"):
            ids["PatentesId"].append(processo["Id"])

    for processo in dados.get("ProcessosPatenteInternacional", []):
        if processo.get("Id"):
            ids["PatentesInternacionalId"].append(
                processo["Id"]
            )

    return ids
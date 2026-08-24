import pandas as pd


df_processos = pd.read_csv(
    "processos.csv"
)

df_envolvidos = pd.read_csv(
    "processos_envolvidos.csv"
)


print("=" * 60)
print("VALIDAÇÃO DOS DADOS APOL")
print("=" * 60)

print("\nPROCESSOS")
print("-" * 60)

print("Linhas:", len(df_processos))
print("Colunas:", len(df_processos.columns))

print("\nValores nulos:")
print(df_processos.isnull().sum())

print("\nDuplicidade de ID:")
print(df_processos["Id"].duplicated().sum())


print("\nENVOLVIDOS")
print("-" * 60)

print("Linhas:", len(df_envolvidos))
print("Colunas:", len(df_envolvidos.columns))

print("\nValores nulos:")
print(df_envolvidos.isnull().sum())

print("\nDuplicidade Processo + Envolvido:")
print(
    df_envolvidos.duplicated(
        subset=["ProcessoId", "EnvolvidoId"]
    ).sum()
)


print("\nTIPOS DOS DADOS")
print("-" * 60)

print(df_processos.dtypes)


print("\nPRIMEIROS PROCESSOS")
print("-" * 60)

print(
    df_processos[
        [
            "Id",
            "NumeroDoProcesso",
            "Marca",
            "Classe",
            "Situacao",
            "Titular"
        ]
    ].head()
)
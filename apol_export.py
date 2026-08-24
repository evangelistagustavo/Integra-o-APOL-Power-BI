from apol_client import ApolClient
from apol_transform import (
    transformar_processos,
    transformar_envolvidos
)


cliente = ApolClient()

dados = cliente.obter_processos_unificados()

df_processos = transformar_processos(dados)
df_envolvidos = transformar_envolvidos(dados)


# Remove a estrutura aninhada
df_processos = df_processos.drop(
    columns=["Envolvidos"],
    errors="ignore"
)


# Exporta processos
df_processos.to_csv(
    "processos.csv",
    index=False,
    encoding="utf-8-sig"
)


# Exporta envolvidos
df_envolvidos.to_csv(
    "processos_envolvidos.csv",
    index=False,
    encoding="utf-8-sig"
)


print("=" * 60)
print("EXPORTAÇÃO APOL")
print("=" * 60)

print(f"\nProcessos exportados: {len(df_processos)}")
print(f"Envolvidos exportados: {len(df_envolvidos)}")

print("\nArquivos atualizados:")
print("- processos.csv")
print("- processos_envolvidos.csv")
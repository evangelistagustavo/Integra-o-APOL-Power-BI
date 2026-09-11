import sqlite3
import pandas as pd


BANCO = r"C:\Users\gusta\OneDrive\Documentos\GitHub\projeto2\apol.db"


conexao = sqlite3.connect(BANCO)

try:

    df_processos = pd.read_sql_query(
        """
        SELECT *
        FROM vw_processos
        """,
        conexao
    )

    df_envolvidos = pd.read_sql_query(
        """
        SELECT *
        FROM vw_processos_envolvidos
        """,
        conexao
    )

    df_despachos = pd.read_sql_query(
        """
        SELECT *
        FROM vw_despachos
        """,
        conexao
    )

    df_ocorrencias = pd.read_sql_query(
        """
        SELECT *
        FROM vw_ocorrencias
        """,
        conexao
    )

    df_providencias = pd.read_sql_query(
        """
        SELECT *
        FROM vw_providencias
        """,
        conexao
    )

finally:

    conexao.close()
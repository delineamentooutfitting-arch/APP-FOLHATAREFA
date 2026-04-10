import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Registro de Avanço",
    layout="wide"
)

st.title("📋 Registro de Avanço de Fabricação")

# ===== CARREGAR PLANILHA =====
arquivo = "atividades.xlsx"
df = pd.read_excel(arquivo)

# ===== COLUNAS QUE SERÃO EXIBIDAS =====
colunas_exibidas = [
    "MÓDULO",
    "DESENHO",
    "REVISÃO",
    "ELEVAÇÃO",
    "DESCRIÇÃO DO PRODUTO",
    "NOME DO PRODUTO",
    "TAG",
    "TAG-CONTROLSTRUI",
    "Prog %",
    "Peso atividade",
    "REALIZADO",
    "ATIVIDADES / OBSERVAÇÕES"
]

df = df[colunas_exibidas]

# ===== BUSCA NAS 8 PRIMEIRAS COLUNAS =====
st.subheader("🔍 Filtro de informações")

busca = st.text_input(
    "Buscar por Módulo, Desenho, TAG, Produto, etc."
)

if busca:
    filtro = df[
        df.iloc[:, 0:8]
        .astype(str)
        .apply(
            lambda x: x.str.contains(busca, case=False, na=False)
        ).any(axis=1)
    ]
    df_filtrado = df[filtro]
else:
    df_filtrado = df

st.divider()

# ===== TABELA EDITÁVEL =====
st.subheader("✍️ Registro de Realizado e Observações")

df_editado = st.data_editor(
    df_filtrado,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "REALIZADO": st.column_config.NumberColumn(
            "REALIZADO (%)",
            min_value=0,
            max_value=100,
            step=5
        ),
        "ATIVIDADES / OBSERVAÇÕES": st.column_config.TextColumn(
            "ATIVIDADES / OBSERVAÇÕES"
        )
    },
    disabled=[
        col for col in df_filtrado.columns
        if col not in ["REALIZADO", "ATIVIDADES / OBSERVAÇÕES"]
    ]
)

# ===== SALVAR =====
if st.button("💾 Salvar alterações"):
    for idx in df_editado.index:
        df.loc[idx, "REALIZADO"] = df_editado.loc[idx, "REALIZADO"]
        df.loc[idx, "ATIVIDADES / OBSERVAÇÕES"] = df_editado.loc[idx, "ATIVIDADES / OBSERVAÇÕES"]

    df.to_excel(arquivo, index=False)
    st.success("✅ Informações salvas com sucesso!")

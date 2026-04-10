import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="P84 – Processamento",
    layout="wide"
)

st.title("📋 P84 – Registro de Avanço | PROCESSAMENTO")

# ===== Arquivo e aba =====
arquivo = "P84 - FOLHA TAREFA.xlsx"
aba = "FOLHA TAREFA PROCESSAMENTO"

# Ler planilha
df_original = pd.read_excel(arquivo, sheet_name=aba)

# ===== Colunas exibidas =====
colunas_exibidas = [
    "MÓDULO",
    "DESENHO",
    "REVISÃO",
    "ELEVAÇÃO",
    "DESCRIÇÃO DO PRODUTO",
    "NOME DO PRODUTO",
    "TAG",
    "TAG-CONTROLSTRU",
    "Prog %",
    "Peso atividade",
    "REALIZADO",
    "ATIVIDADES / OBSERVAÇÕES"
]

df = df_original[colunas_exibidas].copy()

# ===== Filtro =====
st.subheader("🔎 Filtro")

busca = st.text_input(
    "Buscar por módulo, desenho, produto, TAG, etc."
)

if busca:
    mascara = (
        df.iloc[:, 0:8]
        .astype(str)
        .apply(lambda col: col.str.contains(busca, case=False, na=False))
        .any(axis=1)
    )
    df_filtrado = df[mascara].copy()
else:
    df_filtrado = df.copy()

st.divider()

# ===== Tabela editável =====
st.subheader("✍️ Atualizar Realizado e Observações")

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

# ===== Salvar =====
if st.button("💾 Salvar alterações"):
    for idx in df_editado.index:
        df_original.loc[idx, "REALIZADO"] = df_editado.loc[idx, "REALIZADO"]
        df_original.loc[idx, "ATIVIDADES / OBSERVAÇÕES"] = df_editado.loc[idx, "ATIVIDADES / OBSERVAÇÕES"]

    df_original.to_excel(arquivo, index=False)

    st.success("✅ Atualizações salvas com sucesso!")

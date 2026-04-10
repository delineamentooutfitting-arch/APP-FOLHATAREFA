import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="P84 – Processamento",
    layout="wide"
)

st.title("📋 P84 – Registro de Avanço | PROCESSAMENTO")

# =========================
# ARQUIVO E ABA
# =========================
arquivo = "P84 - FOLHA TAREFA.xlsx"
aba = "FOLHA TAREFA PROCESSAMENTO"

df = pd.read_excel(arquivo, sheet_name=aba)

# =========================
# COLUNAS EXIBIDAS
# =========================
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

df = df[colunas_exibidas]

# =========================
# FILTRO / BUSCA (A–H)
# =========================
st.subheader("🔎 Filtro")

busca = st.text_input(
    "Buscar por módulo, desenho, produto, TAG, etc."
)

if busca:
    filtro = (
        df.iloc[:, 0:8]
        .astype(str)
        .apply(lambda col: col.str.contains(busca, case=False, na=False))
        .any(axis=1)
    )
    df_filtrado = df[filtro]
else:
    df_filtrado = df

st.divider()

# =========================
# TABELA EDITÁVEL
# =========================
st.subheader("✍️ Atualização de Progresso")

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

# =========================
# SALVAR
# =========================
if st.button("💾 Salvar alterações"):
    for idx in df_editado.index:
        df.loc[idx, "REALIZADO"] = df_editado.loc[idx, "REALIZADO"]
        df.loc[idx, "ATIVIDADES / OBSERVAÇÕES"] = df_editado.loc[idx, "ATIVIDADES / OBSERVAÇÕES"]

    df.to_excel(arquivo, index=False)
    st.success("✅ Atualizações salvas com sucesso!")
``

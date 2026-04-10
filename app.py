import streamlit as st
import pandas as pd

st.set_page_config(page_title="P84 – Processamento", layout="wide")
st.title("📋 P84 – Registro de Avanço | PROCESSAMENTO")

# =========================
# ARQUIVO / ABA
# =========================
arquivo = "P84 - FOLHA TAREFA.xlsx"
aba = "FOLHA TAREFA PROCESSAMENTO"

df_original = pd.read_excel(arquivo, sheet_name=aba)

# =========================
# COLUNAS BASE
# =========================
colunas = [
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

df = df_original[colunas].copy()

# =========================
# NORMALIZAÇÃO
# =========================
df["Prog %"] = pd.to_numeric(df["Prog %"], errors="coerce").fillna(0)
df["REALIZADO"] = pd.to_numeric(df["REALIZADO"], errors="coerce").fillna(0)
df["ATIVIDADES / OBSERVAÇÕES"] = df["ATIVIDADES / OBSERVAÇÕES"].fillna("").astype(str)

# =========================
# COLUNAS DE EXIBIÇÃO
# =========================
df["PROG (%)"] = df["Prog %"] * 100
df["RESTANTE (%)"] = (df["PROG (%)"] - df["REALIZADO"]).clip(lower=0)

# =========================
# FILTRO
# =========================
st.subheader("🔎 Filtro")
busca = st.text_input("Buscar por módulo, desenho, produto, TAG, etc.")

if busca:
    mask = (
        df.iloc[:, 0:8]
        .astype(str)
        .apply(lambda col: col.str.contains(busca, case=False, na=False))
        .any(axis=1)
    )
    df_filtrado = df[mask].copy()
else:
    df_filtrado = df.copy()

st.divider()

# =========================
# TABELA
# =========================
colunas_view = [
    "MÓDULO",
    "DESENHO",
    "REVISÃO",
    "ELEVAÇÃO",
    "DESCRIÇÃO DO PRODUTO",
    "NOME DO PRODUTO",
    "TAG",
    "TAG-CONTROLSTRU",
    "PROG (%)",
    "Peso atividade",
    "REALIZADO",
    "RESTANTE (%)",
    "ATIVIDADES / OBSERVAÇÕES"
]

df_filtrado = df_filtrado[colunas_view]

df_editado = st.data_editor(
    df_filtrado,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "PROG (%)": st.column_config.NumberColumn("Prog %", format="%.0f%%"),
        "REALIZADO": st.column_config.NumberColumn(
            "REALIZADO (%)",
            min_value=0,
            max_value=100,
            step=5,
        ),
        "RESTANTE (%)": st.column_config.NumberColumn(
            "RESTANTE (%)",
            format="%.0f%%",
        ),
        "ATIVIDADES / OBSERVAÇÕES": st.column_config.TextColumn(
            "ATIVIDADES / OBSERVAÇÕES"
        ),
    },
    disabled=[
        col for col in colunas_view
        if col not in ["REALIZADO", "ATIVIDADES / OBSERVAÇÕES"]
    ],
)

# =========================
# SALVAR
# =========================
if st.button("💾 Salvar alterações"):
    for idx in df_editado.index:
        df_original.loc[idx, "REALIZADO"] = df_editado.loc[idx, "REALIZADO"]
        df_original.loc[idx, "ATIVIDADES / OBSERVAÇÕES"] = df_editado.loc[
            idx, "ATIVIDADES / OBSERVAÇÕES"
        ]

    df_original.to_excel(arquivo, index=False)
    st.success("✅ Atualizações salvas com sucesso!")
``

import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="P84 – Processamento",
    layout="wide"
)

st.title("📋 P84 – Registro de Avanço | PROCESSAMENTO")

# =========================
# ARQUIVO / ABA
# =========================
arquivo = "P84 - FOLHA TAREFA.xlsx"
aba = "FOLHA TAREFA PROCESSAMENTO"

df_original = pd.read_excel(arquivo, sheet_name=aba)

# =========================
# COLUNAS BASE DO EXCEL
# =========================
colunas_base = [
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

df = df_original[colunas_base].copy()

# =========================
# NORMALIZAÇÃO DE TIPOS
# =========================
df["Prog %"] = pd.to_numeric(df["Prog %"], errors="coerce").fillna(0)
df["REALIZADO"] = pd.to_numeric(df["REALIZADO"], errors="coerce").fillna(0)
df["ATIVIDADES / OBSERVAÇÕES"] = (
    df["ATIVIDADES / OBSERVAÇÕES"]
    .fillna("")
    .astype(str)
)

# =========================
# COLUNAS DE EXIBIÇÃO
# =========================
df["PROG (%)"] = df["Prog %"] * 100
df["RESTANTE (%)"] = (df["PROG (%)"] - df["REALIZADO"]).clip(lower=0)

# =========================
# FILTRO (A–H)
# =========================
st.subheader("🔎 Filtro")
busca = st.text_input(
    "Buscar por módulo, desenho, produto, TAG, etc."
)

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
# ORDEM FINAL DAS COLUNAS
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

# Recalcular RESTANTE com base no REALIZADO ATUAL (inclusive editado)
df_filtrado["RESTANTE (%)"] = (
    df_filtrado["PROG (%)"] - df_filtrado["REALIZADO"]
).clip(lower=0)

df_filtrado = df_filtrado[colunas_view]

# =========================
# TABELA EDITÁVEL (MOBILE-FIRST)
# =========================
st.subheader("✍️ Atualizar Realizado e Observações")

df_editado = st.data_editor(
    df_filtrado,
    use_container_width=True,
    hide_index=True,          # 🔥 essencial no celular
    num_rows="fixed",
    column_config={
        "PROG (%)": st.column_config.NumberColumn(
            "Prog %",
            format="%.0f%%"
        ),
        "REALIZADO": st.column_config.NumberColumn(
            "REALIZADO (%)",
            min_value=0,
            max_value=100,
            step=5,
            help="Toque aqui para editar"
        ),
        "RESTANTE (%)": st.column_config.NumberColumn(
            "RESTANTE (%)",
            format="%.0f%%"
        ),
        "ATIVIDADES / OBSERVAÇÕES": st.column_config.TextColumn(
            "OBSERVAÇÕES",
            help="Toque aqui para editar"
        ),
    },
    disabled=[
        col for col in colunas_view
        if col not in ["REALIZADO", "ATIVIDADES / OBSERVAÇÕES"]
    ],
)

# =========================
# SALVAR NO EXCEL (VERSÃO DEFINITIVA)
# =========================
if st.button("💾 Salvar alterações"):

    # 🔒 Garantir tipos corretos ANTES de salvar
    df_original["REALIZADO"] = pd.to_numeric(
        df_original["REALIZADO"], errors="coerce"
    ).fillna(0)

    df_original["ATIVIDADES / OBSERVAÇÕES"] = (
        df_original["ATIVIDADES / OBSERVAÇÕES"]
        .fillna("")
        .astype(str)
    )

    # ✅ Salvar usando alinhamento de índice
    df_original.loc[
        df_editado.index, "REALIZADO"
    ] = df_editado["REALIZADO"]

    df_original.loc[
        df_editado.index, "ATIVIDADES / OBSERVAÇÕES"
    ] = df_editado["ATIVIDADES / OBSERVAÇÕES"].astype(str)

    df_original.to_excel(arquivo, index=False)

    st.success("✅ Atualizações salvas com sucesso!")


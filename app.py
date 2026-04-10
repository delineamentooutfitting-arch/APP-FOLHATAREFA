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
# ARQUIVO
# =========================
arquivo = "P84 - FOLHA TAREFA.xlsx"

# =========================
# LEITURA SEGURA DA ABA
# (evita erro se o nome mudar)
# =========================
xls = pd.ExcelFile(arquivo)

# tenta achar a aba que contenha "PROCESSAMENTO"
aba_processamento = None
for aba in xls.sheet_names:
    if "PROCESSAMENTO" in aba.upper():
        aba_processamento = aba
        break

if aba_processamento is None:
    st.error("❌ Nenhuma aba de PROCESSAMENTO encontrada no Excel.")
    st.stop()

df_original = pd.read_excel(arquivo, sheet_name=aba_processamento)

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
# COLUNAS CALCULADAS (%)
# =========================
df["PROG (%)"] = df["Prog %"] * 100

# =========================
# FILTRO
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

# =========================
# REORDENAR E RECALCULAR RESTANTE
# (sempre depois da edição)
# =========================
df_filtrado["RESTANTE (%)"] = (
    df_filtrado["PROG (%)"] - df_filtrado["REALIZADO"]
).clip(lower=0)

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

st.divider()
st.subheader("✍️ Atualizar Realizado e Observações")

# =========================
# TABELA EDITÁVEL (MOBILE-FIRST)
# =========================
df_editado = st.data_editor(
    df_filtrado,
    use_container_width=True,
    hide_index=True,
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
# SALVAR (VERSÃO DEFINITIVA)
# =========================
if st.button("💾 Salvar alterações"):

    # garantir tipos corretos no original
    df_original["REALIZADO"] = pd.to_numeric(
        df_original["REALIZADO"], errors="coerce"
    ).fillna(0)

    df_original["ATIVIDADES / OBSERVAÇÕES"] = (
        df_original["ATIVIDADES / OBSERVAÇÕES"]
        .fillna("")
        .astype(str)
    )

    # salvar apenas colunas editáveis alinhandas por índice
    df_original.loc[df_editado.index, "REALIZADO"] = df_editado["REALIZADO"]
    df_original.loc[
        df_editado.index, "ATIVIDADES / OBSERVAÇÕES"
    ] = df_editado["ATIVIDADES / OBSERVAÇÕES"].astype(str)

    df_original.to_excel(arquivo, index=False)

    st.success("✅ Atualizações salvas com sucesso!")

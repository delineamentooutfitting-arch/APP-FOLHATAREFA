import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(page_title="P84 – Processamento", layout="wide")
st.title("📋 P84 – Registro de Avanço | PROCESSAMENTO")

arquivo = "P84 - FOLHA TAREFA.xlsx"

# =========================
# LEITURA SEGURA DA ABA
# =========================
xls = pd.ExcelFile(arquivo)
aba = next(
    (s for s in xls.sheet_names if "PROCESSAMENTO" in s.upper()),
    None,
)

if aba is None:
    st.error("❌ Aba de PROCESSAMENTO não encontrada.")
    st.stop()

df_original = pd.read_excel(arquivo, sheet_name=aba)

# =========================
# COLUNAS BASE
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
    "ATIVIDADES / OBSERVAÇÕES",
]

df = df_original[colunas_base].copy()

# =========================
# NORMALIZAÇÃO
# =========================
df["Prog %"] = pd.to_numeric(df["Prog %"], errors="coerce").fillna(0)
df["REALIZADO"] = pd.to_numeric(df["REALIZADO"], errors="coerce").fillna(0)
df["ATIVIDADES / OBSERVAÇÕES"] = df["ATIVIDADES / OBSERVAÇÕES"].fillna("").astype(str)

# =========================
# COLUNAS CALCULADAS
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
        .apply(lambda c: c.str.contains(busca, case=False, na=False))
        .any(axis=1)
    )
    df_view = df[mask].copy()
else:
    df_view = df.copy()

# =========================
# ORDEM DAS COLUNAS
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
    "ATIVIDADES / OBSERVAÇÕES",
]

df_view = df_view[colunas_view]

st.divider()
st.subheader("✍️ Atualizar Realizado e Observações")

# =========================
# DATA EDITOR (MOBILE-FIRST)
# =========================
df_editado = st.data_editor(
    df_view,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "PROG (%)": st.column_config.NumberColumn("Prog %", format="%.0f%%"),
        "REALIZADO": st.column_config.NumberColumn(
            "REALIZADO (%)", min_value=0, max_value=100, step=5
        ),
        "RESTANTE (%)": st.column_config.NumberColumn(
            "RESTANTE (%)", format="%.0f%%"
        ),
        "ATIVIDADES / OBSERVAÇÕES": st.column_config.TextColumn(
            "OBSERVAÇÕES"
        ),
    },
    disabled=[
        c for c in colunas_view
        if c not in ["REALIZADO", "ATIVIDADES / OBSERVAÇÕES"]
    ],
)

# =========================
# SALVAR + RERUN ✅
# =========================
if st.button("💾 Salvar alterações"):

    df_original["REALIZADO"] = pd.to_numeric(
        df_original["REALIZADO"], errors="coerce"
    ).fillna(0)

    df_original["ATIVIDADES / OBSERVAÇÕES"] = (
        df_original["ATIVIDADES / OBSERVAÇÕES"]
        .fillna("")
        .astype(str)
    )

    df_original.loc[df_editado.index, "REALIZADO"] = df_editado["REALIZADO"]
    df_original.loc[
        df_editado.index, "ATIVIDADES / OBSERVAÇÕES"
    ] = df_editado["ATIVIDADES / OBSERVAÇÕES"]

    df_original.to_excel(arquivo, index=False)

    st.success("✅ Atualizações salvas com sucesso!")
    st.rerun()  # 🔥 ESSENCIAL

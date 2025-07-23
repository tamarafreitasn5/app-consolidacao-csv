import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Consulta por CNPJ", layout="wide")
st.title("🔍 Consulta de Contatos por CNPJ")
st.write("Faça upload da planilha Excel, selecione a coluna de CNPJ e digite o CNPJ para buscar contatos.")

def limpar_cnpj(cnpj):
    if pd.isna(cnpj):
        return ''
    return re.sub(r'\D', '', str(cnpj))  # remove tudo que não for número

uploaded_file = st.file_uploader("📂 Carregue a planilha Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        abas = xls.sheet_names
        df_total = pd.DataFrame()

        for aba in abas:
            df = pd.read_excel(xls, sheet_name=aba, dtype=str, header=0)
            df.columns = [col.strip() if isinstance(col, str) else f"Sem nome: {df.columns.get_loc(col)}" for col in df.columns]
            df["Origem"] = aba
            df_total = pd.concat([df_total, df], ignore_index=True)

        st.success(f"✅ {len(abas)} abas carregadas, {len(df_total)} linhas no total.")

        coluna_cnpj = st.selectbox("🧾 Selecione a coluna que contém o CNPJ:", df_total.columns)

        # Limpar CNPJs
        df_total["CNPJ_LIMPO"] = df_total[coluna_cnpj].apply(limpar_cnpj)

        # Entrada do usuário
        cnpj_input = st.text_input("Digite o CNPJ (sem pontuação ou só parte):")

        if cnpj_input:
            cnpj_input_limpo = limpar_cnpj(cnpj_input)

            resultado = df_total[df_total["CNPJ_LIMPO"].str.contains(cnpj_input_limpo, na=False)]

            if resultado.empty:
                st.warning("Nenhum contato encontrado com esse CNPJ.")
                st.write("⚠️ Verifique se digitou o CNPJ sem pontos ou traços. Exemplo: 7975989000106")
                st.write("🧪 CNPJs disponíveis para teste:")
                st.dataframe(df_total[["CNPJ_LIMPO", "Origem"]].drop_duplicates())
            else:
                st.success(f"🎯 {len(resultado)} contatos encontrados.")
                st.dataframe(resultado.drop(columns=["CNPJ_LIMPO"]), use_container_width=True)
        else:
            st.info("Digite o CNPJ para buscar os contatos.")

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    st.info("Faça upload de uma planilha Excel para começar.")

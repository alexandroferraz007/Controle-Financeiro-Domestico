import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Meu Controle Financeiro", layout="wide")
st.title("💰 Controle Financeiro Pessoal")

# --- SIMULAÇÃO DE DADOS (Substitua pela conexão com Google Sheets/Supabase) ---
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "Data", "Tipo", "Categoria", "Descricao", "Valor", "Status"
    ])

# --- BARRA LATERAL: NOVO LANÇAMENTO ---
with st.sidebar:
    st.header("Novo Lançamento")
    with st.form("form_lancamento", clear_on_submit=True):
        data_lanc = st.date_input("Data", value=date.today())
        tipo = st.selectbox("Tipo", ["Saída", "Entrada"])
        categoria = st.selectbox("Categoria", [
            "Alimentação", "Moradia", "Transporte", "Lazer", "Salário", "Investimentos", "Outros"
        ])
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
        
        # Define automaticamente como Agendado se a data for futura
        status_padrao = "Agendado" if data_lanc > date.today() else "Efetivado"
        status = st.selectbox("Status", ["Efetivado", "Agendado"], index=0 if status_padrao=="Efetivado" else 1)
        
        enviado = st.form_submit_button("Salvar Lançamento")
        
        if enviado:
            novo_registro = pd.DataFrame([{
                "Data": pd.to_datetime(data_lanc),
                "Tipo": tipo,
                "Categoria": categoria,
                "Descricao": descricao,
                "Valor": valor,
                "Status": status
            }])
            st.session_state.dados = pd.concat([st.session_state.dados, novo_registro], ignore_index=True)
            st.success("Lançamento registrado!")

# --- ÁREA PRINCIPAL: ANÁLISES E GRÁFICOS ---
df = st.session_state.dados

if not df.empty:
    df["Data"] = pd.to_datetime(df["Data"])
    
    # Separação entre realizado e futuro
    efetivados = df[df["Status"] == "Efetivado"]
    agendados = df[df["Status"] == "Agendado"]

    # Métricas principais (KPIs)
    entradas = efetivados[efetivados["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = efetivados[efetivados["Tipo"] == "Saída"]["Valor"].sum()
    saldo = entradas - saidas
    futuro_saidas = agendados[agendados["Tipo"] == "Saída"]["Valor"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Entradas (Efetivadas)", f"R$ {entradas:,.2f}")
    col2.metric("Saídas (Efetivadas)", f"R$ {saidas:,.2f}")
    col3.metric("Saldo Atual", f"R$ {saldo:,.2f}")
    col4.metric("Contas Agendadas (Saídas)", f"R$ {futuro_saidas:,.2f}", delta_color="inverse")

    st.divider()

    # Gráficos com Plotly
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Gastos por Categoria")
        df_saidas = efetivados[efetivados["Tipo"] == "Saída"]
        if not df_saidas.empty:
            fig_pizza = px.pie(df_saidas, values="Valor", names="Categoria", hole=0.4)
            st.plotly_chart(fig_pizza, use_container_width=True)

    with c2:
        st.subheader("Fluxo de Caixa (Efetivado vs Agendado)")
        fig_bar = px.bar(df, x="Data", y="Valor", color="Tipo", barmode="group", facet_col="Status")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabela de Lançamentos
    st.subheader("Histórico e Programações Futuras")
    st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)
else:
    st.info("Use o menu lateral para adicionar seu primeiro lançamento financeiro.")

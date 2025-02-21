import streamlit as st
import pandas as pd
import plotly.express as px

# --- Pagina config --- 
ANO = 2023
CIDADE = ["Tokyo", "Yokohama", "Osaka"]
DATA_URL = "https://raw.githubusercontent.com/lsouzadasilva/datasets/main/store_sales_2022-2023.csv"


st.set_page_config(page_title='Sales Dashboad', page_icon="📈")
st.title("Relatorio de Vendas")

# --- Ocult menus ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


@st.cache_data 
# --- O decorator @st.cache_data armazena em cache o resultado da função, então se a função for chamada novamente com o mesmo data_url, 
#ela retornará o resultado armazenado em cache em vez de baixar os dados novamente.---
def load_data():
    df = pd.read_csv(DATA_URL)
    df["date_of_sale"] = pd.to_datetime(df["date_of_sale"])
    df = df.sort_values("date_of_sale")
    df["month"] = df["date_of_sale"].dt.month
    df["year"] = df["date_of_sale"].dt.year
    df["year_month"] = df["date_of_sale"].apply(lambda x: str(x.year) + "-" + str(x.month))
    return df

df = load_data()
# st.dataframe(df, use_container_width=True)

vendas_cidade = (
    df.groupby(['city', 'year'])['sales_amount']
    .sum()
    .unstack()
    .assign(change=lambda x: x.pct_change(axis=1)[ANO] * 100) # percentual de diferença comparado ao YEAR  
)

col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        label=CIDADE[0], 
        value=f"$ {vendas_cidade.loc[CIDADE[0], ANO]:,.2f}", 
        delta=f"{vendas_cidade.loc[CIDADE[0], 'change']:.2f}% vs. Last Year",
    )

with col2:
    st.metric(
        label=CIDADE[1], 
        value=f"$ {vendas_cidade.loc[CIDADE[1], ANO]:,.2f}", 
        delta=f"{vendas_cidade.loc[CIDADE[1], 'change']:.2f}% vs. Last Year",
    )

with col3:
    st.metric(
        label=CIDADE[2], 
        value=f"$ {vendas_cidade.loc[CIDADE[2], ANO]:,.2f}", 
        delta=f"{vendas_cidade.loc[CIDADE[2], 'change']:.2f}% vs. Last Year",
    )


cidades = st.selectbox("Escolha uma cidade", CIDADE)
ano = st.toggle("Ultimo ano")
if ano:
    visualizar_ano = ANO - 1
else:
    visualizar_ano = ANO
st.write(f"***Vendas {visualizar_ano}***")


tab_mes, tab_categoria, tab_percent_categoria, tab_linha_tendencia = st.tabs(["Vendas por mês", "Vendas por categoria", "Representação de mercado", "Exportação de dados"])


with tab_mes:
    filtro_mes = (
        df.query("city == @cidades & year == @visualizar_ano")
        .groupby("year_month", dropna=False, as_index=False)["sales_amount"]
        .sum()
    )
fig1 = px.bar(filtro_mes, x="year_month", y="sales_amount", text_auto=True)
fig1.update_traces(textfont_size=10, textangle=0, textposition="outside", cliponaxis=False)
tab_mes.plotly_chart(fig1)


with tab_categoria:
    filtro_categoria = (
        df.query("city == @cidades & year == @visualizar_ano")
        .groupby("product_category", dropna=False, as_index=False)["sales_amount"]
        .sum()
        .sort_values("sales_amount")
    )
fig2 = px.bar(filtro_categoria, x="product_category", y="sales_amount", text_auto=True, text='sales_amount')
fig2.update_traces(textfont_size=10, textangle=0, textposition="outside", cliponaxis=False, texttemplate='%{text:.2s}')
# fig2 = px.bar(filtro_categoria, x="product_category", y="sales_amount", text_auto=True)
# fig2.update_traces(textfont_size=10, textangle=0, textposition="outside", cliponaxis=False)
tab_categoria.plotly_chart(fig2)

with tab_percent_categoria:
    filtro_percent_categoria = (
        df.query("city == @cidades & year == @visualizar_ano")
        .groupby("product_category", dropna=False, as_index=False)["sales_amount"]
        .sum()
    )
fig3 = px.pie(filtro_percent_categoria, values="sales_amount", names="product_category", hole=0.5)
tab_percent_categoria.plotly_chart(fig3)


with tab_linha_tendencia:
    filtro_linha_tendencia = (
        df.query("city == @cidades & year == @visualizar_ano")
        .groupby(["product_category", "product_name","city", "year_month"], dropna=False, as_index=False)["sales_amount"]
        .sum()
        .sort_values("sales_amount", ascending=False)
    )

    # Definir max_value dinamicamente com base nos dados
    max_sales = filtro_linha_tendencia["sales_amount"].max()

    # Exibição com barra de progresso
    fig4 = st.dataframe(
        filtro_linha_tendencia,
        column_config={
            "sales_amount": st.column_config.ProgressColumn(
                "sales_amount", format="$%.2f", min_value=0, max_value=max_sales
            )
        }
    )

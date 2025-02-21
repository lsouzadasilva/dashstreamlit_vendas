import streamlit as st
import pandas as pd

# --- Pagina config --- 
ANO = 2023
CIDADE = ["Tokyo", "Osaka", "Yokohama"]
DATA_URL = "https://raw.githubusercontent.com/Sven-Bo/datasets/master/store_sales_2022-2023.csv"


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
def load_data(data_url):
    return pd.read_csv(data_url).assign(
        date_of_sale = lambda df: pd.to_datetime(df["date_of_sale"]),
        month=lambda df: df["date_of_sale"].dt.month,
        year=lambda df: df["date_of_sale"].dt.year
    )

df = load_data(DATA_URL)
# st.dataframe(df, use_container_width=True)



city_revenue = (
    df.groupby(['city', 'year'])['sales_amount']
    .sum()
    .unstack()
    .assign(change=lambda x: x.pct_change(axis=1)[ANO] * 100) # percentual de diferença comparado ao YEAR
)
# st.dataframe(city_revenue, use_container_width=True)


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=CIDADE[0], 
        value=f"$ {city_revenue.loc[CIDADE[0], ANO]:,.2f}", 
        delta=f"{city_revenue.loc[CIDADE[0], 'change']:.2f}% vs. Last Year",
    )

with col2:
    st.metric(
        label=CIDADE[1], 
        value=f"$ {city_revenue.loc[CIDADE[1], ANO]:,.2f}", 
        delta=f"{city_revenue.loc[CIDADE[1], 'change']:.2f}% vs. Last Year",
    )


with col3:
    st.metric(
        label=CIDADE[2], 
        value=f"$ {city_revenue.loc[CIDADE[2], ANO]:,.2f}", 
        delta=f"{city_revenue.loc[CIDADE[2], 'change']:.2f}% vs. Last Year",
    )


select_city = st.selectbox("Selecione a cidade", CIDADE)
selecione_ano = st.toggle("Ultimo ano")
if selecione_ano:
    visualizar_ano = ANO - 1
else:
    visualizar_ano = ANO
st.write(f"**Vendas {visualizar_ano}**")

mes, categoria = st.tabs(["Analise por mês", "Analise por categoria"])


with mes:
    filtered_data = (
    df.query("city == @select_city & year == @visualizar_ano")
    .groupby("month", dropna=False, as_index=False)["sales_amount"]
    .sum()
    )
    st.bar_chart(
        filtered_data.set_index("month")["sales_amount"],
    )

with categoria:
    filtered_data = (
    df.query("city == @select_city & year == @visualizar_ano")
    .groupby("product_category", dropna=False, as_index=False)["sales_amount"]
    .sum()
    )
    st.bar_chart(
        filtered_data.set_index("product_category")["sales_amount"],
    )
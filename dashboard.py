import pandas as pd, streamlit as st, altair as alt
#carregando os bancos de dados
dataset = pd.read_excel('coffee_sales.xlsx')
by_coffee = pd.read_csv('by_coffee.csv')
by_hour = pd.read_csv('by_hour.csv')
by_month_coffee = pd.read_csv('by_month_coffee.csv')
by_month = pd.read_csv('by_month.csv')
by_time_of_day = pd.read_csv('by_time_of_day.csv')
by_weekday = pd.read_csv('by_weekday.csv')
pv_coffee_month = pd.read_csv('pd_coffee_month.csv')

#calculando valores
ticket = dataset['money'].mean()
payments = dataset['cash_type'].value_counts(normalize=True) * 100
invoicing = dataset['money'].sum()
m1 = by_month['money'].mean() #media mensal


#inicio do dashboard
st.set_page_config(page_title='☕ Dashboard Café', layout='wide')
st.title('☕ Análise de vendas - Cafeteria em Cape Town')
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Faturamento total", f"R{invoicing:,.2f}")
with col2:
    st.metric("Media mensal", f"R{m1:,.2f}")
with col3:
    st.metric("Ticket médio", f"R{ticket:,.2f}")
st.divider()
st.subheader('Faturamento total em cada mês')

by_month.columns = by_month.columns.str.lower()
month_order = by_month['month_year_text'].unique()
by_month['month_year_text'] = pd.Categorical(
    by_month['month_year_text'],
    categories=month_order,
    ordered=True
)
by_month['meta'] = by_month['money'].apply(lambda x: 'Abaixo da média' if x < m else 'Acima da média')
colors = alt.Scale(domain=['Abaixo da média', 'Acima da média'], range=['red','green'])
graph1 = alt.Chart(by_month).mark_bar().encode(
    x=alt.X('month_year_text', sort=list(month_order), title='Mês'),
    y=alt.Y('money', title='Faturamento'),
    color=alt.Color('meta',scale=colors, title='Legenda'),
    tooltip=['month_year_text', 'money']
)
st.altair_chart(graph1, use_container_width=True)

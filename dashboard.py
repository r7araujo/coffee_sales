import pandas as pd, streamlit as st, altair as alt
#carregando os bancos de dados
dataset = pd.read_excel('coffee_sales.xlsx')
by_coffee = pd.read_csv('by_coffee.csv')
by_hour = pd.read_csv('by_hour.csv')
by_month = pd.read_csv('by_month.csv')
by_time_of_day = pd.read_csv('by_time_of_day.csv')
by_weekday = pd.read_csv('by_weekday.csv')
pv_coffee_month = pd.read_csv('pv_coffee_month.csv')
pv_coffee_month.rename(columns={pv_coffee_month.columns[0]: 'Coffee_name'}, inplace=True)

#calculando valores
ticket = dataset['money'].mean()
payments = dataset['cash_type'].value_counts(normalize=True) * 100
invoicing = dataset['money'].sum()
m1 = by_month['money'].mean()   #media mensal
deviation_money = by_month['money'].std()   #desvio padrao mensal
deviation_percentage = (deviation_money / m1)

#inicio do dashboard
st.set_page_config(page_title='☕ Dashboard Café', layout='wide')
st.title('☕ Análise de vendas - Cafeteria em Cape Town')
st.divider()
col_fat, col_m1, col_ticket = st.columns(3)
with col_fat:
    st.metric("Faturamento total", f"R{invoicing:,.2f}")
with col_m1:
    st.metric("Media mensal", f"R{m1:,.2f}")
with col_ticket:
    st.metric("Ticket médio", f"R{ticket:,.2f}")
st.divider()

#grafico de faturamento mensal    
by_month.columns = by_month.columns.str.lower()
month_order = by_month['month_year_text'].unique()
by_month['month_year_text'] = pd.Categorical(
    by_month['month_year_text'],
    categories=month_order,
    ordered=True
)
by_month['meta'] = by_month['money'].apply(lambda x: 'Abaixo da média' if x < m1 else 'Acima da média')
colors = alt.Scale(domain=['Abaixo da média', 'Acima da média'], range=['red','green'])
graph1 = alt.Chart(by_month).mark_bar().encode(
    x=alt.X('month_year_text', sort=list(month_order), title='Mês'),
    y=alt.Y('money', title='Faturamento'),
    color=alt.Color('meta',scale=colors, title='Legenda'),
    tooltip=['month_year_text', 'money']
)
if deviation_percentage < 0.15:
    classification = "✅ Estável"
    texto_explicativo = "Suas vendas são muito constantes."
    cor_delta = "normal"
elif deviation_percentage < 0.30:
    classification = "⚠️ Moderada"
    texto_explicativo = "Fique atento aos meses de baixa."
    cor_delta = "off"
else:
    classification = "⚡ Alta Volatilidade"
    texto_explicativo = "Pode haver forte sazonalidade ou eventos atípicos."
    cor_delta = "inverse"
min_deviation = m1 - deviation_money
max_deviation = m1 + deviation_money

col_graph1, col_deviation = st.columns([2,1])
with col_graph1:
    st.subheader('Faturamento total em cada mês')
    st.altair_chart(graph1, use_container_width=True)
with col_deviation:
    st.subheader('Análise de risco')
    st.metric(
        label='Volatilidade das vendas',
        value=f'{deviation_percentage:.0%}',
        delta=classification,
        delta_color = 'inverse'
    )
    st.write('O que esperar no mês?')
    st.info(f'O faturamento deve ficar entre: R{min_deviation:,.0f} e R{max_deviation:,.0f}.')

#heatmap e receita total por café
long_coffee_month = pv_coffee_month.melt(
    id_vars=['Coffee_name'],
    var_name='mes',
    value_name='faturamento'
)

graph2 = alt.Chart(by_coffee).mark_bar().encode(
    x=alt.X('coffee_name', sort='y', title='Tipo de café'),
    y=alt.Y('money', title='Faturamento total'),
    color=alt.Color('money', title='Vendas', scale=alt.Scale(scheme='greens')),
    tooltip=['coffee_name', 'money']
)
by_units = dataset['coffee_name'].value_counts().reset_index()
by_units.columns = ['coffee_name', 'units']
to_scatter = pd.merge(by_coffee,by_units, on='coffee_name')
scatter = alt.Chart(to_scatter).mark_circle(size=150).encode(
    x=alt.X('units', title='Unidades vendidas'),
    y=alt.Y('money', title='Faturamento'),
    color=alt.Color('coffee_name', legend=None),
    tooltip=['coffee_name','units','money']
).interactive()
texts = scatter.mark_text(dy=-15).encode(
    text='coffee_name'
)
graph3 = scatter + texts
col_total_coffee, col_infos = st.columns([2,1])
with col_total_coffee:
    st.subheader('Faturamento por café')
    st.altair_chart(graph2, use_container_width=True)
with col_infos:
    st.altair_chart(graph3, use_container_width=True)

top_list = []
top_coffee = []
for coffee in long_coffee_month['Coffee_name'].unique():
    data_coffee = long_coffee_month[long_coffee_month['Coffee_name'] == coffee]
    mean_coffee = data_coffee['faturamento'].mean()
    deviation_coffee = data_coffee['faturamento'].std()
    top = mean_coffee + (2 * deviation_coffee)
    top_month = data_coffee[data_coffee['faturamento'] > top]
    for _, row in top_month.iterrows():
        name_date = pd.to_datetime(row['mes'])
        name_date = name_date.strftime('%b-%Y')
        top_list.append(f'{coffee} teve um pico em {name_date}')
        top_coffee.append(coffee)
graph4 = alt.Chart(long_coffee_month[long_coffee_month['Coffee_name'].isin(top_coffee)]).mark_line().encode(
    x=alt.X('mes', title='Mês'),
    y=alt.Y('faturamento', title='Faturamento'),
    color=alt.Color('Coffee_name',title='Café')   
)
st.subheader('Destaques e anomalias')

col_lines, col_top_coffees = st.columns([2,1])

with col_lines:
    st.altair_chart(graph4, use_container_width=True)
with col_top_coffees:
    if top_list:
        st.write('Meses em que algum café teve destaque: ')
        for mensagem in top_list:
            st.info(mensagem)
    else:
        st.success('Não houve pico de vendas ou anomalia para nenhum café.')

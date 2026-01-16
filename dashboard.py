import pandas as pd, streamlit as st, altair as alt, plotly.express as px, plotly.graph_objects as go
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

st.set_page_config(page_title='☕ Dashboard Café', layout='wide')
st.title('☕ Análise de vendas - Cafeteria em Cape Town')
st.divider()
dashboard, details = st.tabs(["📊 Dashboard", "📝 Explicação"])
with dashboard:
    #inicio do dashboard
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

    m2 = by_weekday['money'].mean()
    by_weekday['meta'] = by_weekday['money'].apply(lambda x: 'Abaixo da média' if x < (m2 * 0.8) else ('Acima da média' if x > (m2 * 1.2) else 'Na média'))
    colors2 = alt.Scale(domain=['Abaixo da média', 'Acima da média', 'Na média'], range=['red','green','blue'])
    graph5 = alt.Chart(by_weekday).mark_bar().encode(
        x=alt.X('Weekday', title='Dia da semana'),
        y=alt.Y('money', title='Faturamento'),
        color=alt.Color('meta', scale=colors2, title='Legenda'),
        tooltip=['Weekday', 'money']
    )
    tot_by_time = by_time_of_day[['Morning','Afternoon','Night']].sum().reset_index()
    tot_by_time.columns = ['periodo', 'total']
    graph6 = px.pie(
        tot_by_time,
        values='total',
        names='periodo'
    )
    st.subheader('Vendas em dias de semana e períodos do dia')
    col_weekday, col_timeday = st.columns([2,1])
    with col_weekday:
        st.altair_chart(graph5, use_container_width=True)
    with col_timeday:
        st.plotly_chart(graph6)
with details:
    st.subheader('1. Faturamento anual:')
    st.markdown('A empresa apresenta volatilidade considerada moderada para o setor,' \
    'tendo influência da sazonalidade - gerada pelas estações do ano, por exemplo.')
    st.subheader('2. Análise de produtos:')
    st.markdown('Latte e Americano with milk representam cerca de 41% do faturamento total, ' \
    'sendo produtos extremamentes importantes para a loja.')
    st.markdown('Os produtos apresentam uma dispersão equilibrada. O que significa opções equilibradas para o cliente. ')
    st.markdown('Espresso: produto mais barato do cardápio, não representa a maior parte das vendas, ' \
    'mas pode ser mantido pela facilidade de produção e pela possibilidade de atrair clientes.')
    st.subheader('3. Destaques e anomalias: ')
    st.markdown('Para visualizar as anomalias de vendas positivas (2 vezes mais do que a média mensal daquele produto), ' \
    'seriam necessários dados de pelo menos dois anos para estabelecer uma correlação.')
    st.subheader('4. Vendas em dias de semana e períodos do dia: ')
    st.markdown('Os produtos não vendem mais no fim de semana do que durante a semana.' \
    'As vendas são consistentes, o que favorece a análise de que é um negócio com maior demanda de locais.')
    st.markdown('As vendas estão definitivamente equilibradas entre os 3 períodos do dia.')
    st.subheader('5. Sugestões: ')
    st.markdown('Considerando a análise de que o negócio tem maior demanda de locais,' \
    'poderiam se implementar promoções de acordo com os horários do dia. ' \
    'Por exemplo promoção de espresso no período da manhã - até 10h, ' \
    'gerando mais vendas e atraindo mais clientes que podem se tornar frequentes futuramente.')
    st.markdown('Há duas estratégias de marketing: placas e banners, focando no público local que transita na região frequentemente ou ' \
    'anúncios personalizados nas redes sociais, voltados para o público que busca uma experiência ao ir em uma cafeteria.')
    st.markdown('A implementação de bebidas elaboradas podem gerar retornos positivos, ' \
    'para o público que busca uma experiência e não uma bebida do cotidiano.')
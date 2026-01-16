# Coffee Shop Sales Dashboard ☕

Este projeto é um dashboard interativo desenvolvido em Python para analisar as vendas de uma cafeteria. O objetivo é identificar padrões de consumo por horário (Manhã, Tarde, Noite) e analisar a eficiência financeira dos produtos.
O banco de dados foi retirado do Kaggle

## 📊 Funcionalidades do Projeto

- **Análise Temporal:** Visualização do volume de vendas dividido por períodos do dia.
- **Matriz de Eficiência:** Gráfico de dispersão (Scatter Plot) classificando produtos em "Alto Retorno" vs "Baixa Eficiência" baseando-se no Ticket Médio.
- **KPIs Dinâmicos:** Cálculo automático de representatividade de vendas (ex: Latte e Americano).

## 🛠️ Tecnologias Utilizadas

- **Python** (Linguagem Principal)
- **Streamlit** (Framework de Dashboard)
- **Pandas** (Manipulação de Dados)
- **Altair & Plotly** (Visualização de Dados)

## 🚀 Como rodar o projeto localmente

1. Clone o repositório:
   ```bash
   git clone [https://github.com/r7araujo/coffee_sales.git](https://github.com/r7araujo/coffee_sales.git)
2. Instale as dependências:
    ```bash
    pip install -r requirements.txt
3. Execute o streamlit:
    ```bash
    streamlit run dashboard.py

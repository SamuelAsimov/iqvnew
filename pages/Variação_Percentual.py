#Importando as bibliotecas necessarias
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import secrets
import altair as alt


#setando a configuração da pagina
st.set_page_config(layout='wide')

st.title("Matriz de Evolução")


    


query_nota = f'''SELECT bairro_nome, questao, nome_resposta_origem, etapa, inicio_pesquisa, resposta, id FROM V_Resposta_Nota 
WHERE resposta > 0 

    '''

# Initialize connection.
conn = st.connection('mysql', type='sql')
df_nota = conn.query(query_nota, ttl=100)


# Crie a nova coluna 'qtd_respostas_etapa'
df_nota['qtd_respostas_etapa'] = df_nota.groupby(['etapa', 'bairro_nome'])['id'].transform('count')/30

df_nota['significancia'] = np.where(df_nota['qtd_respostas_etapa'] > 20, 'Significante', 'Amostra Baixa')

filtro_significancia = st.sidebar.multiselect('Selecione o a quantidade de amostras', df_nota['significancia'].unique())
if filtro_significancia:
    df_nota=df_nota[df_nota['significancia'].isin(filtro_significancia)]


etapa_selecionada = st.sidebar.selectbox('etapa', df_nota['etapa'].unique())





if etapa_selecionada == 1:
    st.text('Etapa invalida')
else:
   

    # Filtrar o DataFrame para incluir apenas a etapa desejada e a etapa anterior
    df_filtrado = df_nota[df_nota['etapa'].isin([etapa_selecionada, etapa_selecionada - 1])]


    # Criar tabelas pivot para as duas etapas
    tabela_comparativa = pd.pivot_table(df_filtrado, values='resposta', index='bairro_nome', columns=['etapa', 'questao'], aggfunc=np.mean)

    # Preencher valores NaN com 0, caso haja bairros sem respostas em alguma questão
    tabela_comparativa.fillna(0, inplace=True)

    # Calcular a variação percentual entre as duas etapas
    tabela_variacao = ((tabela_comparativa[etapa_selecionada] - tabela_comparativa[etapa_selecionada - 1]) / tabela_comparativa[etapa_selecionada - 1]) 

    # Arredondar os valores para uma casa decimal
    tabela_variacao = tabela_variacao.round(4)

    tabela_variacao = tabela_variacao[tabela_variacao != -1].dropna()
    # Função para aplicar a formatação condicional
    def destaca_valores(val):
        
        cor = 'color: green' if val > 0 else 'color: red' if val < 0 else ''
        return cor
    # Aplicar formatação condicional à tabela
    tabela_variacao_destacada = tabela_variacao.style.applymap(destaca_valores).format("{:.1%}")

    st.dataframe(tabela_variacao_destacada)


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

conn = st.connection('mysql', type='sql')
# 1. as sidebar menu

    
# Perform query.
# Execute a consulta SQL para obter a menor e a maior data
query_data = 'SELECT MIN(inicio_pesquisa) AS menor_data, MAX(inicio_pesquisa) AS maior_data FROM V_Resposta_Nota;'
df_data = conn.query(query_data, ttl=600)

querry_etapas = 'SELECT DISTINCT etapa FROM V_Resposta_Nota'
df_etapas = conn.query(querry_etapas, ttl=600)


with st.sidebar.expander('Data da pesquisa'):
    data_filtro = st.date_input('Selecione a Data', (df_data['menor_data'].min(), df_data['maior_data'].max()))

#Criando os filtros
filtro_etapa = st.sidebar.multiselect('Selecione a etapa', df_etapas['etapa'])


if filtro_etapa:
    query_nota = f'''SELECT bairro_nome, questao, nome_resposta_origem, etapa, inicio_pesquisa, resposta, id FROM V_Resposta_Nota 
    WHERE resposta > 0 
    AND inicio_pesquisa BETWEEN '{data_filtro[0]}' AND '{data_filtro[1]}' 
    AND etapa IN ({', '.join(map(str, filtro_etapa))})
    '''
else:
    # Se a lista filtro_etapa estiver vazia, retorna tudo
    query_nota = f'''SELECT bairro_nome, questao, nome_resposta_origem, etapa, inicio_pesquisa, resposta, id FROM V_Resposta_Nota 
    WHERE resposta > 0 
    AND inicio_pesquisa BETWEEN '{data_filtro[0]}' AND '{data_filtro[1]}'
    '''

df_nota = conn.query(query_nota, ttl=100)

 # Criar tabelas pivot para as duas etapas
tab_matriz = pd.pivot_table(df_nota, values='resposta', index='bairro_nome', columns=['questao'], aggfunc=np.mean)
#tab_matriz.fillna(0, inplace=True)

def destaca_valores(val):
        
        cor = 'color: green' if val > 6 else 'color: red' if val < 6 else ''
        return cor
tab_matriz = tab_matriz.style.applymap(destaca_valores)

st.data_editor(tab_matriz, use_container_width=True, height=600)


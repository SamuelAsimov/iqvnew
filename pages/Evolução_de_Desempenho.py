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

st.title("Matriz de Notas")

# 1. as sidebar menu


conn = st.connection('mysql', type='sql')

# Se a lista filtro_etapa estiver vazia, retorna tudo
query_nota = f'''SELECT bairro_nome, questao, nome_resposta_origem, etapa, inicio_pesquisa, resposta, id FROM V_Resposta_Nota 
    WHERE resposta > 0 
    '''

df_nota = conn.query(query_nota, ttl=600)

col1, col2, col3 = st.columns([3,3, 1])

with col1:
    filtro_questao_1=st.selectbox('Escolha a questão 1', df_nota['questao'].unique())
    if filtro_questao_1:
        df_filtrado_1=df_nota[df_nota['questao']==filtro_questao_1]

    media_notas_por_etapa = df_filtrado_1.groupby('etapa')['resposta'].mean()
    evolucao_df = pd.DataFrame({
    'etapa': media_notas_por_etapa.index,
    'media_nota': media_notas_por_etapa.values
    })
    chart = alt.Chart(evolucao_df).mark_line(point=True).encode(
    x='etapa',
    y=alt.Y('media_nota', scale=alt.Scale(domain=[evolucao_df['media_nota'].min()-0.2, evolucao_df['media_nota'].max()+0.2]))
    ).interactive()
    
    st.altair_chart(chart, theme="streamlit", use_container_width=True)

    filtro_questao_3=st.selectbox('Escolha a questão 3', df_nota['questao'].unique())
    if filtro_questao_3:
        df_filtrado_3=df_nota[df_nota['questao']==filtro_questao_3]

    media_notas_por_etapa_3 = df_filtrado_3.groupby('etapa')['resposta'].mean()
    evolucao_df_3 = pd.DataFrame({
    'etapa': media_notas_por_etapa_3.index,
    'media_nota': media_notas_por_etapa_3.values
    })
    chart2 = alt.Chart(evolucao_df_3).mark_line(point=True).encode(
    x='etapa',
    y=alt.Y('media_nota', scale=alt.Scale(domain=[evolucao_df_3['media_nota'].min()-0.2, evolucao_df_3['media_nota'].max()+0.2]))
    ).interactive()
    
    st.altair_chart(chart2, theme="streamlit", use_container_width=True)

with col2:
    filtro_questao_2=st.selectbox('Escolha a questão 2', df_nota['questao'].unique())
    if filtro_questao_2:
        df_filtrado_2=df_nota[df_nota['questao']==filtro_questao_2]

    media_notas_por_etapa_2 = df_filtrado_2.groupby('etapa')['resposta'].mean()
    evolucao_df = pd.DataFrame({
    'etapa': media_notas_por_etapa_2.index,
    'media_nota': media_notas_por_etapa_2.values
    })

    chart = alt.Chart(evolucao_df).mark_line(point=True).encode(
    x='etapa',
    y=alt.Y('media_nota', scale=alt.Scale(domain=[evolucao_df['media_nota'].min()-0.2, evolucao_df['media_nota'].max()+0.2]))
    ).interactive()
    
    st.altair_chart(chart, theme="streamlit", use_container_width=True)

    ################################################################################################################################################
    filtro_questao_4=st.selectbox('Escolha a questão 4', df_nota['questao'].unique())
    if filtro_questao_4:
        df_filtrado_4=df_nota[df_nota['questao']==filtro_questao_4]

    media_notas_por_etapa_4 = df_filtrado_4.groupby('etapa')['resposta'].mean()
    evolucao_df_4 = pd.DataFrame({
    'etapa': media_notas_por_etapa_4.index,
    'media_nota': media_notas_por_etapa_4.values
    })

    chart_4 = alt.Chart(evolucao_df_4).mark_line(point=True).encode(
    x='etapa',
    y=alt.Y('media_nota', scale=alt.Scale(domain=[evolucao_df_4['media_nota'].min()-0.2, evolucao_df_4['media_nota'].max()+0.2]))
    ).interactive()
    
    st.altair_chart(chart_4, theme="streamlit", use_container_width=True)
# Ajustando o layout do gráfico


    

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


@st.cache_data 

def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

#setando a configuração da pagina
st.set_page_config(layout='wide', page_title="Nota de Avaliação dos Serviços da Prefeitura")

st.title("Amostras de Avaliação dos Serviços da Prefeitura")

    
# Initialize connection.
conn = st.connection('mysql', type='sql')
# Perform query.
# Execute a consulta SQL para obter a menor e a maior data
query_data = 'SELECT MIN(inicio_pesquisa) AS menor_data, MAX(inicio_pesquisa) AS maior_data FROM V_Resposta_Nota;'
df_data = conn.query(query_data, ttl=600)

querry_etapas = 'SELECT DISTINCT etapa FROM V_Resposta_Nota'
df_etapas = conn.query(querry_etapas, ttl=600)



###################


with st.sidebar.expander('Data da pesquisa'):
    data_filtro = st.date_input('Selecione a Data', (df_data['menor_data'].min(), df_data['maior_data'].max()))

#Criando os filtros
filtro_etapa = st.sidebar.multiselect('Selecione a etapa', df_etapas['etapa'])
   

if filtro_etapa:
    query_nota = f'''SELECT bairro_nome, nome_resposta_origem, etapa, inicio_pesquisa, id FROM V_Resposta_Nota 
    
    WHERE inicio_pesquisa BETWEEN '{data_filtro[0]}' AND '{data_filtro[1]}' 
    AND etapa IN ({', '.join(map(str, filtro_etapa))})
    '''
else:
    # Se a lista filtro_etapa estiver vazia, retorna tudo
    query_nota = f'''SELECT bairro_nome, nome_resposta_origem, etapa, inicio_pesquisa, id FROM V_Resposta_Nota 
        
        WHERE inicio_pesquisa BETWEEN '{data_filtro[0]}' AND '{data_filtro[1]}'
    '''

df_nota = conn.query(query_nota, ttl=100)

# Crie a nova coluna 'qtd_respostas_etapa'
df_nota['qtd_respostas_etapa'] = df_nota.groupby(['etapa', 'bairro_nome'])['id'].transform('count')/30

df_nota['significancia'] = np.where(df_nota['qtd_respostas_etapa'] > 20, 'Significante', 'Amostra Baixa')


query_ponderacao = f'''SELECT nome_bairro, inicio_pesquisa, nome_resposta_origem,id FROM V_Respostas_Ponderacao 
                     '''


df_alocacao = conn.query(query_ponderacao, ttl=100)


filtro_significancia = st.sidebar.multiselect('Selecione o a quantidade de amostras', df_nota['significancia'].unique())
if filtro_significancia:
    df_nota=df_nota[df_nota['significancia'].isin(filtro_significancia)]




base_normal_amostra = alt.Chart(df_nota).encode(
    x=alt.X('count():Q').title(""),
    y=alt.Y('bairro_nome', bandPosition=0.4).sort('-x').title(""),
    color=alt.Color('nome_resposta_origem:N').title("Resposta origem")   # Adicione o valor da barra como texto
) 
font_size=18

fig_amostra_normal = (base_normal_amostra.mark_bar(size=20, cornerRadiusTopRight=10, cornerRadiusBottomRight=10)).properties(
    height=2000
).configure_axis(
    labelFontSize=font_size,
    titleFontSize=font_size,
    labelLimit=700
).configure_text(
    fontSize=font_size,
    align='right',
    dx=5,
    color='black'
)
###############################################################
base_alocacao_amostra = alt.Chart(df_alocacao).encode(
    x=alt.X('count()/30:Q').title(""),
    y=alt.Y('nome_bairro', bandPosition=0.4).sort('-x').title(""),
    color=alt.Color('nome_resposta_origem:N').title("Resposta origem")   # Adicione o valor da barra como texto
) 
font_size=18

fig_amostra_alocacao = (base_alocacao_amostra.mark_bar(size=20, cornerRadiusTopRight=10, cornerRadiusBottomRight=10)).properties(
    height=2000
).configure_axis(
    labelFontSize=font_size,
    titleFontSize=font_size,
    labelLimit=700
).configure_text(
    fontSize=font_size,
    align='right',
    dx=5,
    color='black'
)

quantidade_respostas=round(len(df_nota) / 30)

aba1, aba2 = st.tabs(['Amostra Notas', 'Amostra Alocação'])
with aba1:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown("<h1 style='text-align: center;'>Amostra notas</h1>", unsafe_allow_html=True)
        with col2:
             st.metric("Quantidade de respostas", quantidade_respostas)
        st.altair_chart(fig_amostra_normal, use_container_width=True)

# Plotando o gráfico no Streamlit
with aba2:
        st.markdown("<h1 style='text-align: center;'>Amostra alocação</h1>", unsafe_allow_html=True)
        st.altair_chart(fig_amostra_alocacao, use_container_width=True)

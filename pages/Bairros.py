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

st.title("Notas de Avaliação dos Serviços da Prefeitura por Bairro")
# 1. as sidebar menu

# Initialize connection.
conn = st.connection('mysql', type='sql')
conn_2 = st.connection('mysql_2', type='sql')

query_pop= "SELECT * FROM pop_itajuba"
pop_bairro = conn_2.query(query_pop, ttl=600)
# Perform query.
# Execute a consulta SQL para obter a menor e a maior data
query_data = 'SELECT MIN(inicio_pesquisa) AS menor_data, MAX(inicio_pesquisa) AS maior_data FROM V_Resposta_Nota;'
df_data = conn.query(query_data, ttl=600)

querry_etapas = 'SELECT DISTINCT etapa FROM V_Resposta_Nota'
df_etapas = conn.query(querry_etapas, ttl=600)

querry_questao_nota= 'SELECT DISTINCT questao FROM V_Resposta_Nota'
df_questao_nota = conn.query(querry_questao_nota, ttl=600)


querry_questao_alocacao= 'SELECT DISTINCT questao FROM V_Respostas_Ponderacao'
df_questao_aloca = conn.query(querry_questao_alocacao, ttl=600)


###################


with st.sidebar.expander('Data da pesquisa'):
    data_filtro = st.date_input('Selecione a Data', (df_data['menor_data'].min(), df_data['maior_data'].max()))

#Criando os filtros
filtro_etapa = st.sidebar.multiselect('Selecione a etapa', df_etapas['etapa'])
   
##Criando os filtros
filtro_questao_nota = st.sidebar.multiselect('Selecione a questão avaliação', sorted(df_questao_nota['questao']))

filtro_questao_aloca = st.sidebar.multiselect('Selecione a questão alocação', sorted(df_questao_aloca['questao']))

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

#colocando a população nas notas
df_nota=df_nota.merge(pop_bairro, left_on='bairro_nome', right_on='Bairro')
# Crie a nova coluna 'qtd_respostas_etapa'
df_nota['qtd_respostas_etapa'] = df_nota.groupby(['etapa', 'bairro_nome'])['id'].transform('count')/30
df_nota['peso']=df_nota['Populacao']/df_nota['qtd_respostas_etapa']
df_nota['significancia'] = np.where(df_nota['qtd_respostas_etapa'] > 20, 'Significante', 'Amostra Baixa')


query_ponderacao = f'''SELECT resposta, questao, nome_bairro, inicio_pesquisa, nome_resposta_origem,id FROM V_Respostas_Ponderacao 
                    WHERE resposta > 0 '''


df_alocacao = conn.query(query_ponderacao, ttl=100)


if filtro_questao_nota:
    df_nota=df_nota[df_nota['questao'].isin(filtro_questao_nota)]
    
if filtro_questao_aloca:
    df_alocacao=df_alocacao[df_alocacao['questao'].isin(filtro_questao_aloca)]

filtro_significancia = st.sidebar.multiselect('Selecione o a quantidade de amostras', df_nota['significancia'].unique())
if filtro_significancia:
    df_nota=df_nota[df_nota['significancia'].isin(filtro_significancia)]

##################Criando as tabelas para as imagens##########################################
# Calcule a média ponderada por questão
df_media_ponderada = (df_nota['resposta'] * df_nota['peso']).groupby(df_nota['bairro_nome']).sum() / df_nota.groupby('bairro_nome')['peso'].sum()
df_media_ponderada = df_media_ponderada.sort_values(ascending= False)
tab_media_ponderada = pd.DataFrame({'bairro_nome': df_media_ponderada.index, 'media_ponderada': df_media_ponderada.values}).sort_values('media_ponderada', ascending= True)


tab_media_normal = df_nota.groupby('bairro_nome')[['resposta']].mean().sort_values('resposta', ascending= True).reset_index()
tab_media_alocacao = df_alocacao.groupby('nome_bairro')[['resposta']].mean().sort_values('resposta', ascending= True).reset_index()

font_size = 18 

linha_media_normal = alt.Chart(tab_media_normal).mark_rule(color='red').encode(
    x='mean(resposta)',
)

# Criar gráfico de barras com linha de regra para a média
base_normal = alt.Chart(tab_media_normal).encode(
    x=alt.X('resposta').title(""),
    y=alt.Y('bairro_nome', bandPosition=0.4).sort('-x').title(""),
    text=alt.Text('resposta:N', format='.2f')   # Adicione o valor da barra como texto
) 

fig_media_normal = (base_normal.mark_bar(size=20) + base_normal.mark_text(align='left') + linha_media_normal).properties(
    height=1200
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


# Criar gráfico de barras com linha de regra para a média ponderada
linha_media_ponderada = alt.Chart(tab_media_ponderada).mark_rule(color='red').encode(
    x='mean(media_ponderada)',
)

base_normal_ponderada = alt.Chart(tab_media_ponderada).encode(
    x=alt.X('media_ponderada').title(""),
    y=alt.Y('bairro_nome', bandPosition=0.4).sort('-x').title(""),
    text=alt.Text('media_ponderada:N', format='.2f')   # Adicione o valor da barra como texto
) 

fig_media_ponderada = (base_normal_ponderada.mark_bar(size=20) + base_normal_ponderada.mark_text(align='left') + linha_media_ponderada).properties(
    height=1200
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
# Criar gráfico de barras com linha de regra para a média da alocação

# Criar gráfico de barras com linha de regra para a média ponderada
linha_media_alocacao = alt.Chart(tab_media_alocacao).mark_rule(color='red').encode(
    x='mean(resposta)',
)

base_normal_alocacao = alt.Chart(tab_media_alocacao).encode(
    x=alt.X('resposta').title(""),
    y=alt.Y('nome_bairro', bandPosition=0.4).sort('-x').title(""),
    text=alt.Text('resposta:N', format='.2f')   # Adicione o valor da barra como texto
) 

fig_media_alocacao = (base_normal_alocacao.mark_bar(size=20) + base_normal_alocacao.mark_text(align='left') + linha_media_alocacao).properties(
    height=1200
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

##Visualização
aba1, aba2, aba3 = st.tabs(['Média Ponderada', 'Média Normal', 'Alocação de Recursos'])

with aba1:
        # Use the following line to center the title
        st.markdown("<h1 style='text-align: center;'>Media ponderada das notas</h1>", unsafe_allow_html=True)
        st.altair_chart(fig_media_ponderada, use_container_width=True)

# Plotando o gráfico no Streamlit
with aba2:
        st.markdown("<h1 style='text-align: center;'>Media das notas</h1>", unsafe_allow_html=True)
        st.altair_chart(fig_media_normal, use_container_width=True)

with aba3:
         st.markdown("<h1 style='text-align: center;'>Media das alocação de recursos</h1>", unsafe_allow_html=True)
         st.altair_chart(fig_media_alocacao, use_container_width=True)
        
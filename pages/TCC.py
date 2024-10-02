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

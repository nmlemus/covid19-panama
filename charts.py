import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np

from scipy import stats as sps
from scipy.interpolate import interp1d

from matplotlib import pyplot as plt
from matplotlib.dates import date2num, num2date
from matplotlib import dates as mdates
from matplotlib import ticker
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from PIL import Image

def other_charts(st, casos_panama):

    st.title('Numero de Casos vs Pruebas Realizadas')

    casos_pty = casos_panama.copy()
    casos_pty['pctg'] = round(casos_pty.positivity_pctg*100, 1)
    casos_pty['month'] = pd.to_datetime(casos_pty['date'], format='%Y-%m-%d').dt.month_name()

    fig = px.scatter(casos_pty, x="pcr_test", y="new_cases", color="month", labels='date', size='pctg')
    st.plotly_chart(fig)

    st.markdown('Interesante destacar que el comportamiento entre los nuevos casos y el numero de pruebas realizadas es casi lineal. \
        Esto tiene implicaciones directas en los analisis que se pueden hacer de los resultados. Pareciera como que el covid está bastante \
            expandido por Panamá y en la medida que más pruebas se hacen más casos aparecen.')

def letalidad_chart(st, casos_panama):

    st.header('Letalidad')

    casos_pty = casos_panama.copy()
    casos_pty['letalidad'] = round(casos_pty['letalidad']*100, 1)

    fig = px.line(casos_pty, x="fecha", y="letalidad")
    st.plotly_chart(fig)

    # st.markdown('La letalidad del covid ha ido disminuyendo.')

def positivity_chart(st, casos_panama):

    st.header('% de Positividad')

    casos_pty = casos_panama.copy()
    casos_pty['pctg'] = round(casos_pty.pct_positividad*100, 1)

    fig = px.line(casos_pty, x="fecha", y="pctg")
    st.plotly_chart(fig)

    # st.markdown('La letalidad del covid ha ido disminuyendo.')

def any_chart(st, casos_panama, columns, title):

    st.header(title)

    casos_pty = casos_panama.copy()

    fig = px.line(casos_pty, x = columns[0], y = columns[1])
    st.plotly_chart(fig)

def recuperados_activos(st, casos_panama):

    st.header('Total de Casos, Recuperados y Fallecidos')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=casos_panama['fecha'], y=casos_panama['casos_totales'],
                    mode='lines',
                    name='Total Casos'))
    fig.add_trace(go.Scatter(x=casos_panama['fecha'], y=casos_panama['recuperados_totales'],
                    mode='lines',
                    name='Total Recuperados'))
    fig.add_trace(go.Scatter(x=casos_panama['fecha'], y=casos_panama['fallecidos_totales'],
                    mode='lines',
                    name='Total Fallecidos'))
    # fig.update_yaxes(type="log", range=[0,6]) 

    st.plotly_chart(fig)

def letalidad_recuperados_pctg(st, casos_panama):

    st.header('% de Letalidad vs % de Recuperados')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=casos_panama['fecha'], y=casos_panama['letalidad'],
                    mode='lines',
                    name='% de Letalidad'))
    fig.add_trace(go.Scatter(x=casos_panama['fecha'], y=casos_panama['pct_recuperados'],
                    mode='lines',
                    name='% de Recuperados'))
    # fig.update_yaxes(type="log", range=[0,6]) 

    st.plotly_chart(fig)

def dynamic_charts(st, casos_panama):

    st.title('Cree sus propias gráficas')

    st.markdown('Seleccione cualquiera de las columnas de los datos y cree sus propias gráficas.')

    x = st.selectbox('Valor de X', (casos_panama.columns), index=1)

    y = st.selectbox('Valor de Y', (casos_panama.columns), index=2)

    color = st.selectbox('Valor para el Color de Cada punto', (casos_panama.columns), index=12)

    size = st.selectbox('Valor para el Tamaño de cada punto', (casos_panama.columns), index=11)

    fig = px.scatter(casos_panama, x=x, y=y, color=color, size=size)
    st.plotly_chart(fig)
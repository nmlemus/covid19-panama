import plotly.express as px

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

    st.title('Letalidad')

    casos_pty = casos_panama.copy()
    casos_pty['letalidad'] = round(casos_pty.total_death/casos_pty.acumulated_cases*100, 1)

    fig = px.line(casos_pty, x="date", y="letalidad")
    st.plotly_chart(fig)

    st.markdown('La letalidad del covid ha ido disminuyendo.')

def positivity_chart(st, casos_panama):

    st.title('Positivity Rate')

    casos_pty = casos_panama.copy()
    casos_pty['pctg'] = round(casos_pty.positivity_pctg*100, 1)

    fig = px.line(casos_pty, x="date", y="pctg")
    st.plotly_chart(fig)

    # st.markdown('La letalidad del covid ha ido disminuyendo.')
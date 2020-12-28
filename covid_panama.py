import streamlit as st
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

import plotly.express as px

from PIL import Image

from utils import *

image = Image.open('download.jpeg')

st.image(image, use_column_width=True)

objective = set_sidebar(st)

if objective == 'Calculo de Rt':
    calculo_rt(st)
elif objective == 'Documentacion':
    documentation(st)
elif objective == 'Graficas Generales':
    casos_panama = pd.read_excel('/Users/nmlemus/covid19/panama/pruebas_vs_casos.xlsx')
    casos_panama['pctg'] = casos_panama.pctg*100

    fig = px.scatter(casos_panama, x="pruebas", y="positivos", color="month", labels='date', size='pctg')
    st.plotly_chart(fig)
elif objective == 'About me':
    about_me(st)
else:
    inicio(st)
    


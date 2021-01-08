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
from charts import *
from calculo_rt import *

# image = Image.open('images/banner.jpg')

# st.image(image, use_column_width=True)

objective = set_sidebar(st)


@st.cache
def load_data():
    casos_panama = pd.read_excel('data/covid_panama_new.xlsx')
    return casos_panama

# Create a text element and let the reader know the data is loading.
# data_load_state = st.text('Cargando datos...')
# Load 10,000 rows of data into the dataframe.
casos_panama = load_data()
# Notify the reader that the data was successfully loaded.
# data_load_state.text('Datos cargados...!')

if objective == 'Calculo de Rt':
    calculo_rt(st, casos_panama)
elif objective == 'Documentacion':
    documentation(st)
elif objective == 'Graficas Generales':
    other_charts(st, casos_panama)
    letalidad_chart(st, casos_panama)
    positivity_chart(st, casos_panama)
elif objective == 'Sobre mi':
    about_me(st)
else:
    inicio(st, casos_panama)
    


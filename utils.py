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

from datetime import datetime

from charts import *

def set_sidebar(st):
    st.sidebar.title('Tipo de Analsis')
    
    # st.sidebar.subheader('Objective')
    # Add a selectbox to the sidebar:
    objective = st.sidebar.radio(
        '',
        ('Inicio', 'Documentacion', 'Calculo de Rt', 'Graficas Generales', 'Sobre mi'))
    
    return objective

def inicio(st, casos_panama):

    today = datetime.today().strftime('%d-%m-%Y')
    st.title('Covid-19 en Panamá: ' + str(today))
    st.header('Resumen diario')

    df_last_days = casos_panama.sort_values('fecha', ascending=False).head(10)

    df_resumen = pd.DataFrame({
        'Variables': ['Casos totales', 'Fallecidos totales', 'Recuperados totales', 'Casos activos', 'Letalidad', '% de Recuperados'],
        'Valores': [df_last_days.head(1)['casos_totales'].values[0], df_last_days.head(1)['fallecidos_totales'].values[0], \
            df_last_days.head(1)['recuperados_totales'].values[0], df_last_days.head(1)['casos_activos'].values[0], \
                round(df_last_days.head(1)['letalidad'].values[0]*100, 2), round(df_last_days.head(1)['pct_recuperados'].values[0]*100, 1)]
    })

    st.dataframe(df_resumen)

    st.markdown('[Descargar Datos Históricos](https://github.com/nmlemus/covid19-panama/blob/main/data/covid_panama_new.xlsx)')

    letalidad_chart(st, casos_panama)
    positivity_chart(st, casos_panama)

    st.subheader('Datos de los últimos 10 días')
    st.dataframe(df_last_days.style.highlight_max(axis=0))

    st.markdown('[Descargar Datos Históricos](https://github.com/nmlemus/covid19-panama/blob/main/data/covid_panama_new.xlsx)')
    
    
def documentation(st):
    st.markdown('It’s Easter. A couple weeks ago, this was the target for returning to normal. Hospitals are now full of patients, cities bloom as new hotspots, \
         and politicians wrestle with the balance of human and economic costs. We’re left to wonder if we are equipped with the right metrics to guide our path \
             forward. Add to the confusion that metrics are based on noisy data that changes daily. There’s one metric, however, that has the most promise. \
                 It’s called $$R_t$$ – the effective reproduction number. We can estimate it, and it’s the key to getting us through the next few months.')

    st.markdown('Most people are more familiar with $R_0$. $R_0$ is the basic reproduction number of an epidemic. It’s defined as the number of secondary infections produced by a single infection. If R0 is greater than one, the epidemic spreads quickly **. If R0 is less than one, the epidemic spreads, but limps along and disappears before everyone becomes infected. The flu has an R0 between one and two while measles sits in the high teens. While R0 is a useful measure, it is flawed in an important way: it’s static.')

    st.markdown('We’ve all witnessed that humans are adaptable. Our behavior changes, whether mandated or self-prescribed, and that changes the effective R value at any point in time. As we socially distance and isolate, R plummets. Because the value changes so rapidly, Epidemiologists have argued that the only true way to combat COVID19 is to understand and manage by Rt.')

    st.markdown('I agree, and I’d go further: we not only need to know Rt, we need to know local Rt. New York’s epidemic is vastly different than California’s and using a single number to describe them both is not useful. Knowing the local Rt allows us to manage the pandemic effectively.')

    st.markdown('States have had a variety of lockdown strategies, but there’s very little understanding of which have worked and which need to go further. Some states like California have been locked down for weeks, while others like Iowa and Nebraska continue to balk at taking action as cases rise. Being able to compare local Rts between different areas and/or watch how Rt changes in one place can help us measure how effective local policies are at slowing the spread of the virus.')

    st.markdown('Tracking Rt also lets us know when we might loosen restrictions. Any suggestion that we loosen restrictions when Rt > 1.0 is an explicit decision to let the virus proliferate. At the same time, if we are able to reduce Rt to below 1.0, and we can reduce the number of cases overall, the virus becomes manageable. Life can begin to return to ‘normal.’ But without knowing Rt we are simply flying blind.')

    st.markdown('How We Can Calculate Rt. It’s impossible to measure Rt directly, so we have to estimate it. Fortunately, there are many ways to this. One particular method Bettencourt & Ribeiro described in their 2008 paper, “Real Time Bayesian Estimation of the Epidemic Potential of Emerging Infectious Diseases.” This solution caught my attention because it focuses on the same principles from my first post, Predicting Coronavirus Cases. It uses Bayesian statistics to estimate the most likely value of Rt and also return a credible interval for the true value of Rt.')

    st.markdown('What follows is an application of Bettencourt & Ribeiro’s process (with an important modification) to US State COVID19 data. Note that while this post focuses on the high level concepts, those who want to dig in further can find the details in this Jupyter notebook.')

    st.markdown('Bettencourt & Ribeiro’s original algorithm to estimate Rt is a function of how many new cases appear each day. The relationship between the number of cases yesterday and the number of cases today give us a hint of what Rt might be. However, we can’t rely on any one day too much in trying to guess Rt, as daily case counts are imperfect due to changing testing capacity, lags in data reporting, and random chance. However, using Bayes’ Theorem, we can take the new information we get from each day’s case count to adjust our expectation of what Rt is, getting closer to the true value as more daily data becomes available.')

    st.markdown('I applied this algorithm to the data to produce a model for each state’s Rt, and how it changes over time. But I noticed something strange. Over time, all states trended asymptotically to Rt = 1.0, refusing to descend below that value. Somehow, the algorithm wasn’t reflecting the reality that Rt could be < 1.0 as well.')

    st.markdown('To fix this, I made one significant change to their algorithm that maintains the integrity of Bettencourt & Ribeiro’s original work while allowing us to see the real-time picture clearly. The change was simple. Instead of considering every previous day of data we have to estimate Rt, I only use the last seven days. Doing so is mathematically sound and produces more accurate results when the model is compared to actual data, but I admit is not reviewed by anyone. While I invite feedback, I’m sharing these results with that disclaimer well in advance.')
    
def about_me(st):
    
    st.title('Sobre mi')
    
    image = Image.open('images/noel_barcelona.jpg')

    st.image(image, width=200)
    
    st.markdown('My name is Noel Moreno Lemus. I graduated in Radiochemistry from the Higher Institute of Nuclear Science and Technology (ISCTN) in Havana, Cuba (2002). I obtained a master`s degree in Bioinformatics by InsTEC in Havana, Cuba (2007), and a Ph.D. in Computational Modeling at the National Laboratory of Scientific Computing of Rio de Janeiro, Brazil (2013-2018). I also possess the category of assistant professor. I was a professor of Mathematics (2002-2010), at the University of Information Science in Havana, Cuba. At the same time, I was the Head of the Bioinformatics Research Group at UCI, from 2004-2010.')

    st.markdown('I have experience in computer science, with emphasis on Data Science, Artificial Intelligence, mainly in the following areas: DataBase, Data Analysis, Data Mining, Machine Learning, Computational Modeling and Simulation, and Uncertainty Quantification. My current research and work interests focus on Big Data, Data Mining, Machine Learning, Computational Modeling and Simulation, Uncertainty Quantification, and Artificial Intelligence.')

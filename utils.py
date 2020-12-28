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

def set_sidebar(st):
    st.sidebar.title('Tipo de Analsis')
    
    # st.sidebar.subheader('Objective')
    # Add a selectbox to the sidebar:
    objective = st.sidebar.radio(
        '',
        ('Inicio', 'Documentacion', 'Calculo de Rt', 'Graficas Generales', 'About me'))
    
    return objective

def inicio(st):
    st.text('Aqui va el inicio, toda la muela introductoria')
    
    
def calculo_rt(st):
    
    st.title('Covid19 Panama: Calculo de $R_t$')
    
    @st.cache
    def load_data():
        casos_panama = pd.read_excel('/Users/nmlemus/covid19/panama/laprensa_casos_pruebas_time_series.xlsx')
        return casos_panama

    # Create a text element and let the reader know the data is loading.
    data_load_state = st.text('Cargando datos...')
    # Load 10,000 rows of data into the dataframe.
    casos_panama = load_data()
    # Notify the reader that the data was successfully loaded.
    data_load_state.text('Datos cargados...!')

    st.subheader('Datos')
    st.dataframe(casos_panama.style.highlight_max(axis=0))
    #st.write(casos_panama)


    st.subheader('Casos por dia')

    cases = casos_panama.sort_values('date')[['date', 'casos_acumulados']]
    cases['date'] = pd.to_datetime(cases.date, format='%Y-%m-%d')
    cases['casos_acumulados'] = cases.casos_acumulados.astype(float)
    cases = cases.set_index('date')
    cases = pd.Series(cases['casos_acumulados'])

    def prepare_cases(cases, cutoff=25):
        new_cases = cases.diff()

        smoothed = new_cases.rolling(7,
            win_type='gaussian',
            min_periods=1,
            center=True).mean(std=2).round()

        idx_start = np.searchsorted(smoothed, cutoff)

        smoothed = smoothed.iloc[idx_start:]
        original = new_cases.loc[smoothed.index]

        return original, smoothed

    original, smoothed = prepare_cases(cases)

    original.plot(title=f"Panama New Cases per Day",
                   c='k',
                   linestyle=':',
                   alpha=.5,
                   label='Actual',
                   legend=True,
                 figsize=(15, 8))

    ax = smoothed.plot(label='Smoothed',
                       legend=True)

    ax.get_figure().set_facecolor('w')
    st.write(ax.get_figure())

    # Gamma is 1/serial interval
    # https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article
    # https://www.nejm.org/doi/full/10.1056/NEJMoa2001316
    GAMMA = 1/7

    # We create an array for every possible value of Rt
    R_T_MAX = 12
    r_t_range = np.linspace(0, R_T_MAX, R_T_MAX*100+1)

    def get_posteriors(sr, sigma=0.15):

        # (1) Calculate Lambda
        lam = sr[:-1].values * np.exp(GAMMA * (r_t_range[:, None] - 1))


        # (2) Calculate each day's likelihood
        likelihoods = pd.DataFrame(
            data = sps.poisson.pmf(sr[1:].values, lam),
            index = r_t_range,
            columns = sr.index[1:])

        # (3) Create the Gaussian Matrix
        process_matrix = sps.norm(loc=r_t_range,
                                  scale=sigma
                                 ).pdf(r_t_range[:, None]) 

        # (3a) Normalize all rows to sum to 1
        process_matrix /= process_matrix.sum(axis=0)

        # (4) Calculate the initial prior
        #prior0 = sps.gamma(a=4).pdf(r_t_range)
        prior0 = np.ones_like(r_t_range)/len(r_t_range)
        prior0 /= prior0.sum()

        # Create a DataFrame that will hold our posteriors for each day
        # Insert our prior as the first posterior.
        posteriors = pd.DataFrame(
            index=r_t_range,
            columns=sr.index,
            data={sr.index[0]: prior0}
        )

        # We said we'd keep track of the sum of the log of the probability
        # of the data for maximum likelihood calculation.
        log_likelihood = 0.0

        # (5) Iteratively apply Bayes' rule
        for previous_day, current_day in zip(sr.index[:-1], sr.index[1:]):

            #(5a) Calculate the new prior
            current_prior = process_matrix @ posteriors[previous_day]

            #(5b) Calculate the numerator of Bayes' Rule: P(k|R_t)P(R_t)
            numerator = likelihoods[current_day] * current_prior

            #(5c) Calcluate the denominator of Bayes' Rule P(k)
            denominator = np.sum(numerator)

            # Execute full Bayes' Rule
            posteriors[current_day] = numerator/denominator

            # Add to the running sum of log likelihoods
            log_likelihood += np.log(denominator)

        return posteriors, log_likelihood

    # Note that we're fixing sigma to a value just for the example
    posteriors, log_likelihood = get_posteriors(smoothed, sigma=.25)

    def highest_density_interval(pmf, p=.9, debug=False):
        # If we pass a DataFrame, just call this recursively on the columns
        if(isinstance(pmf, pd.DataFrame)):
            return pd.DataFrame([highest_density_interval(pmf[col], p=p) for col in pmf],
                                index=pmf.columns)

        cumsum = np.cumsum(pmf.values)

        # N x N matrix of total probability mass for each low, high
        total_p = cumsum - cumsum[:, None]

        # Return all indices with total_p > p
        lows, highs = (total_p > p).nonzero()

        # Find the smallest range (highest density)
        best = (highs - lows).argmin()

        low = pmf.index[lows[best]]
        high = pmf.index[highs[best]]

        return pd.Series([low, high],
                         index=[f'Low_{p*100:.0f}',
                                f'High_{p*100:.0f}'])

    # Note that this takes a while to execute - it's not the most efficient algorithm
    hdis = highest_density_interval(posteriors, p=.9)

    most_likely = posteriors.idxmax().rename('ML')

    # Look into why you shift -1
    result = pd.concat([most_likely, hdis], axis=1)

    st.markdown('$R_t$ ultimos dias')
    st.dataframe(result.tail().style.highlight_max(axis=0))
    #st.write(result.tail())

    def plot_rt(result, ax, state_name):

        ax.set_title(f"{state_name}")

        # Colors
        ABOVE = [1,0,0]
        MIDDLE = [1,1,1]
        BELOW = [0,0,0]
        cmap = ListedColormap(np.r_[
            np.linspace(BELOW,MIDDLE,25),
            np.linspace(MIDDLE,ABOVE,25)
        ])
        color_mapped = lambda y: np.clip(y, .5, 1.5)-.5

        index = result['ML'].index.get_level_values('date')
        values = result['ML'].values

        # Plot dots and line
        ax.plot(index, values, c='k', zorder=1, alpha=.25)
        ax.scatter(index,
                   values,
                   s=40,
                   lw=.5,
                   c=cmap(color_mapped(values)),
                   edgecolors='k', zorder=2)

        # Aesthetically, extrapolate credible interval by 1 day either side
        lowfn = interp1d(date2num(index),
                         result['Low_90'].values,
                         bounds_error=False,
                         fill_value='extrapolate')

        highfn = interp1d(date2num(index),
                          result['High_90'].values,
                          bounds_error=False,
                          fill_value='extrapolate')

        extended = pd.date_range(start=pd.Timestamp('2020-03-19'),
                                 end=index[-1]+pd.Timedelta(days=1))

        ax.fill_between(extended,
                        lowfn(date2num(extended)),
                        highfn(date2num(extended)),
                        color='k',
                        alpha=.1,
                        lw=0,
                        zorder=3)

        ax.axhline(1.0, c='k', lw=1, label='$R_t=1.0$', alpha=.25);

        # Formatting
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.xaxis.set_minor_locator(mdates.DayLocator())

        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.1f}"))
        ax.yaxis.tick_right()
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.margins(0)
        ax.grid(which='major', axis='y', c='k', alpha=.1, zorder=-2)
        ax.margins(0)
        ax.set_ylim(0.0, 5.0)
        ax.set_xlim(pd.Timestamp('2020-03-19'), result.index.get_level_values('date')[-1]+pd.Timedelta(days=1))
        fig.set_facecolor('w')


    fig, ax = plt.subplots(figsize=(15,8))

    plot_rt(result, ax, 'Panama')
    ax.set_title(f'Real-time $R_t$ for Panama')
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    st.pyplot(fig, dip=100)
    
    
def documentation(st):
    st.markdown('It’s Easter. A couple weeks ago, this was the target for returning to normal. Hospitals are now full of patients, cities bloom as new hotspots, and politicians wrestle with the balance of human and economic costs. We’re left to wonder if we are equipped with the right metrics to guide our path forward. Add to the confusion that metrics are based on noisy data that changes daily. There’s one metric, however, that has the most promise. It’s called $$R_t$$ – the effective reproduction number. We can estimate it, and it’s the key to getting us through the next few months.')

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
    
    st.title('About me')
    
    image = Image.open('noel_barcelona.jpg')

    st.image(image, width=200)
    
    st.markdown('My name is Noel Moreno Lemus. I graduated in Radiochemistry from the Higher Institute of Nuclear Science and Technology (ISCTN) in Havana, Cuba (2002). I obtained a master`s degree in Bioinformatics by InsTEC in Havana, Cuba (2007), and a Ph.D. in Computational Modeling at the National Laboratory of Scientific Computing of Rio de Janeiro, Brazil (2013-2018). I also possess the category of assistant professor. I was a professor of Mathematics (2002-2010), at the University of Information Science in Havana, Cuba. At the same time, I was the Head of the Bioinformatics Research Group at UCI, from 2004-2010.')

    st.markdown('I have experience in computer science, with emphasis on Data Science, Artificial Intelligence, mainly in the following areas: DataBase, Data Analysis, Data Mining, Machine Learning, Computational Modeling and Simulation, and Uncertainty Quantification. My current research and work interests focus on Big Data, Data Mining, Machine Learning, Computational Modeling and Simulation, Uncertainty Quantification, and Artificial Intelligence.')
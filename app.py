import pandas as pd
import plotly.express as px
import streamlit as st

idx = pd.IndexSlice


@st.cache_data
def load_data():
    welfare_params = pd.read_csv('data/welfare-params.csv', index_col=0)
    population = pd.read_csv('data/population.csv', index_col=[0, 1])
    grants = pd.read_csv('data/grants.csv', index_col=0)
    return welfare_params, population, grants


welfare_params, population, grants = load_data()


def plot_df(df, title, ylabel, inv_lim=False):
    fig = px.line(df, labels={'x': '', 'value': ylabel})

    fig.update_layout(
        title=title,
        xaxis=dict(
            range=[df.index.min(), df.index.max()],
        ),
        yaxis=dict(
            range=[df.min().min(), 0] if inv_lim else [0, df.max().max()],
        ),
        legend=dict(
            title='',
            x=0,
            y=0 if inv_lim else 1,
        ),
    )

    return fig


@st.cache_data
def update_species_graphs(countries, user_welfare_params):
    if user_welfare_params.empty:
        tmp_welfare_params = welfare_params
    else:
        tmp_welfare_params = user_welfare_params

    species = tmp_welfare_params.columns

    if not countries:
        tmp_countries = population.index.get_level_values(0).unique().tolist()
    else:
        tmp_countries = countries

    figs = []

    population_by_species = population[species].loc[tmp_countries].groupby(
        'Year').sum().divide(1e9)
    figs.append(plot_df(population_by_species, 'Populations Over Time',
                        'Population (Billions)'))

    capacity = population_by_species.apply(
        lambda x: x*tmp_welfare_params.loc['range', species], axis=1)
    # figs.append(plot_df(capacity, 'Welfare Capacities Over Time',
    #                     'Welfare Capacity (Arbitrary Units)'))

    welfare = capacity.apply(
        lambda x: x*tmp_welfare_params.loc['value', species], axis=1)
    figs.append(plot_df(welfare, 'Total Welfare Over Time',
                        'Total Welfare (Arbitrary Units)', inv_lim=True))

    return figs


@st.cache_data
def update_countries_graphs(countries, user_welfare_params):
    if user_welfare_params.empty:
        tmp_welfare_params = welfare_params
    else:
        tmp_welfare_params = user_welfare_params

    species = tmp_welfare_params.columns

    if not countries:
        tmp_countries = population.index.get_level_values(0).unique().tolist()
        population_by_country = pd.concat([population[species].groupby(
            'Year').sum().divide(1e9)], keys=['World'])
    else:
        tmp_countries = countries
        population_by_country = population[species].loc[tmp_countries].divide(
            1e9)

    figs = []

    figs.append(plot_df(population_by_country.sum(axis=1).unstack(
        0).rename_axis(columns=None), 'Populations Over Time', 'Population (Billions)'))

    capacity = population_by_country.apply(
        lambda x: x*tmp_welfare_params.loc['range'], axis=1)
    # figs.append(plot_df(capacity.sum(axis=1).unstack(
    #     0).sum(axis=1).rename('World'), 'Welfare Capacities Over Time', 'Welfare Capacity (Arbitrary Units'))

    welfare = capacity.apply(
        lambda x: x*tmp_welfare_params.loc['value'], axis=1)
    figs.append(plot_df(welfare.sum(axis=1).unstack(
        0).rename_axis(columns=None), 'Total Welfare Over Time', 'Total Welfare (Arbitrary Units)', inv_lim=True))

    return figs


st.markdown('# Animal Welfare Dashboard')

st.markdown('## Net Global Welfare')

species = st.multiselect('Select Species', welfare_params.columns, default=[
    'Cattle', 'Chickens', 'Pigs', 'Carp', 'Other Fish', 'Shrimp'])
if not species:
    species = welfare_params.columns

with st.expander('Welfare Parameters'):
    range_col, value_col = st.columns(2)
    user_welfare_params = pd.DataFrame(
        index=welfare_params.index, columns=species)
    with range_col:
        st.markdown('### Welfare Range (0 to 1)')
        for col in species:
            user_welfare_params.loc['range', col] = st.slider(
                col, 0.0, 1.0, welfare_params.loc['range', col])

    with value_col:
        st.markdown('### Welfare Value (-1 to 1)')
        for col in species:
            user_welfare_params.loc['value', col] = st.slider(
                col, -1.0, 1.0, welfare_params.loc['value', col])


countries = st.multiselect(
    'Select Countries', population.index.get_level_values(0).unique().tolist(), default=[
        'China', 'India', 'United States of America'])

species_col, country_col = st.columns(2)
with species_col:
    figs = update_species_graphs(countries, user_welfare_params)
    st.markdown('### Species Graphs')
    for fig in figs:
        st.plotly_chart(fig, use_container_width=True)

with country_col:
    figs = update_countries_graphs(countries, user_welfare_params)
    st.markdown('### Country Graphs')
    for fig in figs:
        st.plotly_chart(fig, use_container_width=True)

st.markdown('## Animal Welfare Grants')

st.markdown('### By Organization')

grants_by_org = grants.pivot_table(
    columns='Organization', index='Year', values='Amount', aggfunc='sum')
grants_by_org['Total'] = grants_by_org.sum(axis=1)

st.dataframe(grants_by_org, column_config={
    'Year': st.column_config.NumberColumn(format='%d'),
    **{key: st.column_config.NumberColumn(step=1) for key in grants_by_org.columns}
}, use_container_width=True)

st.markdown('### By Receipient')

grants_by_recipient = grants.groupby(
    'Recipient')['Amount'].sum().sort_values(ascending=False)
st.dataframe(grants_by_recipient, column_config={
    'Recipient': st.column_config.TextColumn(width='large'),
    'Amount': st.column_config.NumberColumn(step=1)
}, use_container_width=True)

st.markdown('### All')

st.dataframe(grants, column_config={
    'Year': st.column_config.NumberColumn(format='%d'),
    'Amount': st.column_config.NumberColumn(step=1)
}, use_container_width=True, hide_index=True)

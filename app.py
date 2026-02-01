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

default_species = [
    'Cattle', 'Chickens', 'Pigs', 'Carp', 'Other Fish', 'Shrimp']

if "species" in st.query_params:
    qp_species = st.query_params.get_all("species")
    if qp_species:
        # Filter to ensure they are valid options
        valid_species = set(welfare_params.columns)
        filtered_species = [s for s in qp_species if s in valid_species]
        if filtered_species:
            default_species = filtered_species

species = st.multiselect('Select Species', welfare_params.columns, default=default_species)
if not species:
    species = welfare_params.columns

with st.expander('Welfare Parameters'):
    range_col, value_col = st.columns(2)
    user_welfare_params = pd.DataFrame(
        index=welfare_params.index, columns=species)
    with range_col:
        st.markdown('### Welfare Range (0 to 1)')
        for col in species:
            default_range = welfare_params.loc['range', col]
            param_key = f"range_{col}"
            if param_key in st.query_params:
                try:
                    # st.query_params returns a string or list. We take the last one if it's a list (though get() handles simple keys).
                    # Actually st.query_params object acts like a dict in newer streamlit versions.
                    val = float(st.query_params[param_key])
                    if 0.0 <= val <= 1.0:
                        default_range = val
                except (ValueError, TypeError):
                    pass
            
            user_welfare_params.loc['range', col] = st.slider(
                col, 0.0, 1.0, default_range)

    with value_col:
        st.markdown('### Welfare Value (-1 to 1)')
        for col in species:
            default_value = welfare_params.loc['value', col]
            param_key = f"value_{col}"
            if param_key in st.query_params:
                try:
                    val = float(st.query_params[param_key])
                    if -1.0 <= val <= 1.0:
                        default_value = val
                except (ValueError, TypeError):
                    pass

            user_welfare_params.loc['value', col] = st.slider(
                col, -1.0, 1.0, default_value)


default_countries = ['China', 'India', 'United States of America']
all_countries = population.index.get_level_values(0).unique().tolist()

if "countries" in st.query_params:
    qp_countries = st.query_params.get_all("countries")
    if qp_countries:
        valid_countries = set(all_countries)
        filtered_countries = [c for c in qp_countries if c in valid_countries]
        if filtered_countries:
            default_countries = filtered_countries

countries = st.multiselect(
    'Select Countries', all_countries, default=default_countries)

# Share Link Logic
import urllib.parse

current_params = {}
if species:
    current_params["species"] = species
if countries:
    current_params["countries"] = countries

# Add welfare parameters for selected species
for col in species:
    # Use the current values from user_welfare_params which were updated by sliders
    r_val = user_welfare_params.loc['range', col]
    v_val = user_welfare_params.loc['value', col]
    current_params[f"range_{col}"] = r_val
    current_params[f"value_{col}"] = v_val

# Update browser URL
# st.query_params.clear()
# st.query_params.update(current_params)

# Generate and display share link
encoded_params = urllib.parse.urlencode(current_params, doseq=True)
# st.context.url returns the URL without query params or anchors
base_url = st.context.url
share_url = f"{base_url}?{encoded_params}"

col_share, col_reset = st.columns([1, 1], gap="small")
with col_share:
    with st.popover("Share", use_container_width=True):
        st.code(share_url, language='text')
with col_reset:
    if st.button("Reset", use_container_width=True):
        st.query_params.clear()
        st.rerun()

species_col, country_col = st.columns(2)
with species_col:
    figs = update_species_graphs(countries, user_welfare_params)
    st.markdown('### Species Graphs')
    for fig in figs:
        st.plotly_chart(fig, width='stretch')

with country_col:
    figs = update_countries_graphs(countries, user_welfare_params)
    st.markdown('### Country Graphs')
    for fig in figs:
        st.plotly_chart(fig, width='stretch')

st.markdown('## Animal Welfare Grants')

st.markdown('### By Organization')

grants_by_org = grants.pivot_table(
    columns='Organization', index='Year', values='Amount', aggfunc='sum')
grants_by_org['Total'] = grants_by_org.sum(axis=1)

st.dataframe(grants_by_org, column_config={
    'Year': st.column_config.NumberColumn(format='%d'),
    **{key: st.column_config.NumberColumn(step=1) for key in grants_by_org.columns}
}, width='stretch')

st.markdown('### By Receipient')

grants_by_recipient = grants.groupby(
    'Recipient')['Amount'].sum().sort_values(ascending=False)
st.dataframe(grants_by_recipient, column_config={
    'Recipient': st.column_config.TextColumn(width='large'),
    'Amount': st.column_config.NumberColumn(step=1)
}, width='stretch')

st.markdown('### All')

st.dataframe(grants, column_config={
    'Year': st.column_config.NumberColumn(format='%d'),
    'Amount': st.column_config.NumberColumn(step=1)
}, width='stretch', hide_index=True)

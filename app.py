import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

color = ["#C15065", "#2C8465", "#BE5915", "#6D3E91", "#CF0A66", "#18470F", "#286BBB", "#883039",
         "#996D39", "#00295B", "#9A5129", "#C4523E", "#A2559C", "#008291", "#578145", "#970046",
         "#00847E", "#B13507", "#4C6A9C", "#00875E", "#B16214", "#8C4569", "#338711", "#D73C50"]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=color)
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams.update({'font.size': 14})

welfare_params = pd.read_csv("data/welfare-params.csv", index_col=0)
population = pd.read_csv("data/population.csv", index_col=[0, 1])


def plot_df(df, title, ylabel, inv_lim=False):
    fig, ax = plt.subplots()
    df.plot(ax=ax)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.spines[['right', 'left']].set_visible(False)
    ax.spines['bottom'].set_visible(
        False) if inv_lim else ax.spines['top'].set_visible(False)
    ax.set_xlim([df.index.min(), df.index.max()])
    ax.set_ylim([df.min().min(), 0]
                if inv_lim else [0, df.max().max()])
    ax.grid(axis='y')
    fig.tight_layout()
    return fig


def update_species_graphs(*slider_values):
    user_welfare_params = pd.DataFrame(np.array(slider_values).reshape(
        2, -1), columns=welfare_params.columns, index=welfare_params.index)

    population_by_species = population.groupby('Year').sum().divide(1e9)
    population_fig = plot_df(population_by_species, "Populations Over Time",
                             "Population (Billions)")

    capacity = population_by_species.apply(
        lambda x: x*user_welfare_params.loc['range'], axis=1)
    capacity_fig = plot_df(capacity, "Welfare Capacities Over Time",
                           "Welfare Capacity (Arbitrary Units)")

    welfare = capacity.apply(
        lambda x: x*user_welfare_params.loc['value'], axis=1)
    welfare_fig = plot_df(welfare, "Total Welfare Over Time",
                          "Total Welfare (Arbitrary Units)", inv_lim=True)

    return [population_fig, capacity_fig, welfare_fig]


def update_country_graphs(countries, *slider_values):
    user_welfare_params = pd.DataFrame(np.array(slider_values).reshape(
        2, -1), columns=welfare_params.columns, index=welfare_params.index)

    population_by_country = population.loc[countries].divide(1e9)
    population_fig = plot_df(population_by_country.sum(axis=1).unstack(
        0).rename_axis(columns=None), "Populations Over Time", "Population (Billions)")

    capacity = population_by_country.apply(
        lambda x: x*user_welfare_params.loc['range'], axis=1)
    capacity_fig = plot_df(capacity.sum(axis=1).unstack(
        0).rename_axis(columns=None), "Welfare Capacities Over Time", "Welfare Capacity (Arbitrary Units)")

    welfare = capacity.apply(
        lambda x: x*user_welfare_params.loc['value'], axis=1)
    welfare_fig = plot_df(welfare.sum(axis=1).unstack(
        0).rename_axis(columns=None), "Total Welfare Over Time", "Total Welfare (Arbitrary Units)", inv_lim=True)

    return [population_fig, capacity_fig, welfare_fig]


with gr.Blocks() as demo:
    gr.Markdown("# Net Global Welfare")

    species_sliders = []
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Welfare Range (0 to 1)")
            for col in welfare_params.columns:
                species_sliders.append(gr.Slider(
                    minimum=0, maximum=1, value=welfare_params.loc['range', col], label=col))

        with gr.Column():
            gr.Markdown("### Welfare Value (-1 to 1)")
            for col in welfare_params.columns:
                species_sliders.append(gr.Slider(
                    minimum=-1, maximum=1, value=welfare_params.loc['value', col], label=col))

    with gr.Row():
        species_population = gr.Plot(show_label=False)
        species_capacity = gr.Plot(show_label=False)
        species_welfare = gr.Plot(show_label=False)

    with gr.Row():
        country_dropdown = gr.Dropdown(
            choices=population.index.get_level_values(0).unique().tolist(),
            value=['China', 'India', 'United States of America'],
            multiselect=True,
            label="Select Countries",
            interactive=True
        )

    with gr.Row():
        country_population = gr.Plot(show_label=False)
        country_capacity = gr.Plot(show_label=False)
        country_welfare = gr.Plot(show_label=False)

    species_graphs = [species_population, species_capacity, species_welfare]
    country_graphs = [country_population, country_capacity, country_welfare]

    for slider in species_sliders:
        slider.release(update_species_graphs,
                       inputs=species_sliders, outputs=species_graphs)

    country_dropdown.change(update_country_graphs, inputs=[country_dropdown] + species_sliders,
                            outputs=country_graphs)

    demo.load(update_species_graphs, inputs=species_sliders,
              outputs=species_graphs)
    demo.load(update_country_graphs, inputs=[country_dropdown] + species_sliders,
              outputs=country_graphs)


demo.launch()

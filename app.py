import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

welfare_params = pd.read_csv("data/welfare-params.csv", index_col=0)
population = pd.read_csv("data/population.csv", index_col=0)


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
    return fig


def update_graphs(*slider_values):
    user_welfare_params = pd.DataFrame(np.array(slider_values).reshape(
        2, -1), columns=welfare_params.columns, index=welfare_params.index)

    population_by_year = population.groupby('Year').sum().divide(1e9)
    fig1 = plot_df(population_by_year, "Populations Over Time",
                   "Population (Billions)")

    capacity = population_by_year.apply(
        lambda x: x*user_welfare_params.loc['range'], axis=1)
    fig2 = plot_df(capacity, "Welfare Capacities Over Time",
                   "Welfare Capacity (Arbitrary Units)")

    welfare = capacity.apply(
        lambda x: x*user_welfare_params.loc['value'], axis=1)
    fig3 = plot_df(welfare, "Total Welfare Over Time",
                   "Total Welfare (Arbitrary Units)", inv_lim=True)

    return fig1, fig2, fig3


with gr.Blocks() as demo:
    gr.Markdown("# Net Global Welfare")

    sliders = []

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Welfare Range (0 to 1)")
            for col in welfare_params.columns:
                sliders.append(gr.Slider(
                    minimum=0, maximum=1, value=welfare_params.loc['range', col], label=col))

        with gr.Column():
            gr.Markdown("### Welfare Value (-1 to 1)")
            for col in welfare_params.columns:
                sliders.append(gr.Slider(
                    minimum=-1, maximum=1, value=welfare_params.loc['value', col], label=col))

    with gr.Row():
        graph1 = gr.Plot()
        graph2 = gr.Plot()
        graph3 = gr.Plot()

    graphs = [graph1, graph2, graph3]

    for slider in sliders:
        slider.release(update_graphs, inputs=sliders, outputs=graphs)

    demo.load(update_graphs, inputs=sliders, outputs=graphs)

demo.launch(share=True)

import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

initial_params = pd.read_csv("data/params.csv", index_col=0)
population = pd.read_csv("data/population.csv", index_col=0).divide(1e9)


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
    return fig


def update_graphs(*slider_values):
    params = pd.DataFrame(np.array(slider_values).reshape(
        2, -1), columns=initial_params.columns, index=initial_params.index)

    fig1 = plot_df(population, "Populations Over Time",
                   "Population (Billions)")

    capacity = population.apply(
        lambda x: x*params.loc['range'], axis=1)
    fig2 = plot_df(capacity, "Welfare Capacities Over Time",
                   "Welfare Capacity (Arbitrary Units)")

    welfare = capacity.apply(lambda x: x*params.loc['value'], axis=1)
    fig3 = plot_df(welfare, "Total Welfare Over Time",
                   "Total Welfare (Arbitrary Units)", inv_lim=True)

    return fig1, fig2, fig3


with gr.Blocks() as demo:
    gr.Markdown("# Net Global Welfare")

    sliders = []

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Welfare Range (0 to 1)")
            for col in initial_params.columns:
                sliders.append(gr.Slider(
                    minimum=0, maximum=1, value=initial_params.loc['range', col], label=col))

        with gr.Column():
            gr.Markdown("### Welfare Value (-1 to 1)")
            for col in initial_params.columns:
                sliders.append(gr.Slider(
                    minimum=-1, maximum=1, value=initial_params.loc['value', col], label=col))

    with gr.Row():
        graph1 = gr.Plot()
        graph2 = gr.Plot()
        graph3 = gr.Plot()

    graphs = [graph1, graph2, graph3]

    for slider in sliders:
        slider.release(update_graphs, inputs=sliders, outputs=graphs)

    demo.load(update_graphs, inputs=sliders, outputs=graphs)

demo.launch(share=True)
